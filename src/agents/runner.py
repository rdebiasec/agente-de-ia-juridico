"""Ejecutor de la firma de agentes con fallback sin API key."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from hashlib import sha1
from typing import Any

from agents import Runner
from agents.lifecycle import RunHooksBase
from agents.run_config import RunConfig

from src.agents.guardrails import (
    apply_output_guardrails,
    check_input,
    needs_human_review,
)
from src.agents.orchestrator import (
    POC_AGENT_ID,
    SPECIALIST_AGENT_IDS,
    build_orchestrator,
    enabled_specialists_for_focus,
)
from src.agents.pipeline import attach_session_continuity, run_post_validations, run_pre_validations
from src.agents.pii import mask_pii
from src.agents.resilience import run_with_retries
from src.agents.session_context import bind_active_session
from src.agents.skill_catalog import agent_display_name
from src.agents.triage import (
    build_triage,
    format_triage_sistema,
    has_penal_context,
    infer_destination_agent,
    is_non_penal_scope_request,
    is_trivial_consultation,
    requires_execution_plan,
)
from src.agents.urgency import format_escalation_notice
from src.config import get_settings
from src.gateway.agent_session import RepositoryAgentSession, reconcile_turn_messages
from src.gateway.expediente import expediente_store
from src.storage import get_repository

logger = logging.getLogger(__name__)


class AgentBudgetExceeded(RuntimeError):
    """El workflow consumió más tokens que el presupuesto configurado."""

_AGENT_SKILL_MAP = {
    "coordinador_expediente_penal": "PEN-COORD",
    "analista_cronologia_hechos_penales": "PEN-HECHOS",
    "analista_tipicidad_y_responsabilidad_penal": "PEN-TIPICIDAD",
    "analista_ruta_procesal_ley906": "PEN-RUTA906",
    "analista_representacion_victimas": "PEN-VICTIMAS",
    "gestor_evidencia_y_soporte_probatorio": "PEN-EVIDENCIA",
    "preparador_estrategico_audiencias_penales": "PEN-AUDIENCIAS",
    "redactor_documentos_juridicos_penales": "PEN-REDACCION",
    "gestor_seguimiento_procesal_penal": "PEN-SEGUIMIENTO",
    "evaluador_derechos_fundamentales_tutela": "PEN-TUTELA",
    "analista_calidad_juridica": "PEN-CALIDAD",
    "fallback": "KAN-FALLBACK",
    "guardrail": "KAN-GUARDRAIL",
    "error": "KAN-ERROR",
}


def _trace_id(session_id: str, message: str) -> str:
    seed = f"{session_id}:{message}:{time.time_ns()}".encode("utf-8")
    return f"tr-{sha1(seed).hexdigest()[:12]}"


def _summarize_input(message: str) -> str:
    normalized = " ".join((message or "").split())
    if len(normalized) <= 160:
        return normalized
    return f"{normalized[:157]}..."


def _truncate(value: str | None, limit: int = 600) -> str:
    text = (value or "").strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _safe_json_preview(payload: Any, limit: int = 900) -> str:
    try:
        dumped = json.dumps(payload, ensure_ascii=False, default=str)
        return _truncate(mask_pii(dumped), limit=limit)
    except Exception:
        return _truncate(mask_pii(str(payload)), limit=limit)


def _extract_input_preview(input_items: list[Any], limit: int = 900) -> str:
    snippets: list[str] = []
    for item in input_items or []:
        if isinstance(item, dict):
            role = item.get("role") or item.get("type") or "item"
            content = item.get("content")
            snippets.append(f"{role}: {_safe_json_preview(content, limit=220)}")
        else:
            snippets.append(_safe_json_preview(item, limit=220))
        if len(" | ".join(snippets)) >= limit:
            break
    return _truncate(" | ".join(snippets), limit=limit)


def _usage_to_dict(usage: Any) -> dict[str, int]:
    if usage is None:
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "cached_input_tokens": 0, "reasoning_tokens": 0}
    input_details = getattr(usage, "input_tokens_details", None)
    output_details = getattr(usage, "output_tokens_details", None)
    return {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
        "cached_input_tokens": int(getattr(input_details, "cached_tokens", 0) or 0),
        "reasoning_tokens": int(getattr(output_details, "reasoning_tokens", 0) or 0),
    }


def _completion_summary(calls: list[dict]) -> dict[str, int]:
    return {
        "calls": len(calls),
        "input_tokens": sum(int(call.get("usage", {}).get("input_tokens", 0) or 0) for call in calls),
        "output_tokens": sum(int(call.get("usage", {}).get("output_tokens", 0) or 0) for call in calls),
        "total_tokens": sum(int(call.get("usage", {}).get("total_tokens", 0) or 0) for call in calls),
    }


class _TraceRunHooks(RunHooksBase[Any, Any]):
    def __init__(self, trace: dict):
        self.trace = trace

    def _span(self, name: str, kind: str, status: str, detail: str) -> None:
        self.trace.setdefault("spans", []).append(
            {
                "name": name,
                "kind": kind,
                "status": status,
                "detail": detail,
                "at_ms": int(time.time() * 1000),
            }
        )

    async def on_agent_start(self, context: Any, agent: Any) -> None:
        self._span(f"agent:{getattr(agent, 'name', 'unknown')}", "agent", "in_progress", "Agente iniciado.")

    async def on_agent_end(self, context: Any, agent: Any, output: Any) -> None:
        preview = _truncate(str(output), limit=120)
        self._span(
            f"agent:{getattr(agent, 'name', 'unknown')}",
            "agent",
            "done",
            f"Agente finalizó. Salida: {preview}",
        )

    async def on_handoff(self, context: Any, from_agent: Any, to_agent: Any) -> None:
        self._span(
            "handoff",
            "handoff",
            "done",
            f"{getattr(from_agent, 'name', '?')} → {getattr(to_agent, 'name', '?')}",
        )
        _append_action(
            self.trace,
            action_type="handoff",
            status="done",
            actor=getattr(from_agent, "name", "coordinador_expediente_penal"),
            detail=f"Handoff hacia {getattr(to_agent, 'name', 'especialista')}.",
        )

    async def on_tool_start(self, context: Any, agent: Any, tool: Any) -> None:
        tool_name = getattr(tool, "name", None) or type(tool).__name__
        self._span(f"tool:{tool_name}", "tool", "in_progress", f"Ejecutando {tool_name}.")
        if tool_name in SPECIALIST_AGENT_IDS:
            self.trace["backoffice_agent"] = tool_name
            _append_action(
                self.trace,
                action_type="backoffice_consult",
                status="in_progress",
                actor=POC_AGENT_ID,
                detail=f"POC consultó equipo interno: {tool_name}.",
            )

    async def on_tool_end(self, context: Any, agent: Any, tool: Any, result: object) -> None:
        tool_name = getattr(tool, "name", None) or type(tool).__name__
        self._span(
            f"tool:{tool_name}",
            "tool",
            "done",
            f"Resultado: {_truncate(_safe_json_preview(result, limit=200))}",
        )
        if tool_name in SPECIALIST_AGENT_IDS:
            _append_action(
                self.trace,
                action_type="backoffice_consult",
                status="done",
                actor=POC_AGENT_ID,
                detail=f"Hallazgos internos de {tool_name} disponibles para síntesis del POC.",
            )

    async def on_llm_start(
        self,
        context: Any,
        agent: Any,
        system_prompt: str | None,
        input_items: list[Any],
    ) -> None:
        started_at_ms = int(time.time() * 1000)
        model_name = getattr(agent, "model", None) or get_settings().openai_model or "default"
        self._span(f"llm:{getattr(agent, 'name', 'unknown')}", "llm", "in_progress", f"Modelo {model_name}.")
        call = {
            "call_id": f"cmp-{len(self.trace['completion']['calls']) + 1}",
            "agent": getattr(agent, "name", "unknown"),
            "model": str(model_name),
            "started_at_ms": started_at_ms,
            "started_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_at_ms / 1000)),
            "system_prompt": _truncate(mask_pii(system_prompt or ""), limit=1400),
            "input_preview": _extract_input_preview(input_items, limit=1200),
            "status": "in_progress",
            "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "cached_input_tokens": 0, "reasoning_tokens": 0},
        }
        self.trace["completion"]["calls"].append(call)

    async def on_llm_end(
        self,
        context: Any,
        agent: Any,
        response: Any,
    ) -> None:
        calls = self.trace["completion"]["calls"]
        if not calls:
            return
        call = calls[-1]
        ended_at_ms = int(time.time() * 1000)
        usage = _usage_to_dict(getattr(response, "usage", None))
        call["response_id"] = getattr(response, "response_id", None)
        call["request_id"] = getattr(response, "request_id", None)
        call["usage"] = usage
        call["ended_at_ms"] = ended_at_ms
        call["duration_ms"] = max(0, ended_at_ms - int(call.get("started_at_ms", ended_at_ms)))
        call["status"] = "done"
        self.trace["completion"]["available"] = True
        token_budget = get_settings().agent_max_total_tokens
        consumed = sum(
            int(item.get("usage", {}).get("total_tokens", 0) or 0)
            for item in calls
        )
        if token_budget > 0 and consumed > token_budget:
            self.trace["completion"]["budget_exceeded"] = True
            raise AgentBudgetExceeded(
                f"Presupuesto de tokens excedido ({consumed}>{token_budget})."
            )
        self._span(
            f"llm:{getattr(agent, 'name', 'unknown')}",
            "llm",
            "done",
            f"Tokens: {usage.get('total_tokens', 0)} (in {usage.get('input_tokens', 0)} / out {usage.get('output_tokens', 0)}).",
        )


def _kan_for_agent(agent_name: str | None) -> str:
    if not agent_name:
        return "KAN-N/A"
    return _AGENT_SKILL_MAP.get(agent_name, "KAN-N/A")


_AGENT_DRAFT_TIPO = {
    "evaluador_derechos_fundamentales_tutela": "tutela",
    "redactor_documentos_juridicos_penales": "documento",
    "preparador_estrategico_audiencias_penales": "audiencia",
    "gestor_seguimiento_procesal_penal": "seguimiento",
    "analista_tipicidad_y_responsabilidad_penal": "analisis_penal",
    "analista_ruta_procesal_ley906": "ruta_procesal",
    "analista_representacion_victimas": "estrategia_victima",
    "gestor_evidencia_y_soporte_probatorio": "plan_probatorio",
    "analista_calidad_juridica": "control_calidad",
    "analista_cronologia_hechos_penales": "cronologia",
}


def _draft_tipo(destination_agent: str) -> str:
    return _AGENT_DRAFT_TIPO.get(destination_agent, "documento")


# Compat: reexporta triage como API interna del runner.
_has_penal_context = has_penal_context
_is_non_penal_scope_request = is_non_penal_scope_request
_infer_destination_agent = infer_destination_agent


def _maybe_create_draft(
    *,
    session_id: str,
    message: str,
    text: str,
    destination_agent: str,
    trace: dict,
) -> str | None:
    """Materializa una salida accionable como borrador HITL y notifica a Slack."""
    try:
        from src.hitl.drafts import crear_borrador, enviar_a_revision
        from src.hitl.slack_review import notificar_borrador

        tipo = _draft_tipo(destination_agent)
        titulo = f"{tipo.capitalize()} · {_summarize_input(message)[:80]}"
        draft = crear_borrador(
            session_id=session_id, contenido=text, tipo=tipo, titulo=titulo
        )
        slack_ts = notificar_borrador(draft)
        if slack_ts:
            enviar_a_revision(draft.id, slack_ts=slack_ts)
        trace["draft_id"] = draft.id
        _append_action(
            trace,
            action_type="draft_created",
            status="pending",
            actor="hitl",
            detail=f"Borrador {draft.id} ({tipo}) creado y pendiente de aprobación del abogado.",
        )
        return draft.id
    except Exception:
        logger.exception("No se pudo registrar el borrador HITL")
        _append_action(
            trace,
            action_type="draft_created",
            status="blocked",
            actor="hitl",
            detail=(
                "No se pudo materializar el borrador para revisión; "
                "la salida NO quedó en cola de aprobación."
            ),
        )
        return None


def _human_review_trace(pending_review: bool, draft_id: str | None) -> tuple[str, str]:
    """status + detalle para la acción/paso de revisión humana."""
    if not pending_review:
        return "done", "No requiere aprobación adicional."
    if draft_id:
        return "pending", "Pendiente de aprobación del abogado."
    return (
        "blocked",
        "Se requería revisión humana pero el borrador NO se materializó; "
        "la salida no quedó en cola de aprobación.",
    )


def _trace_step(step: str, status: str, detail: str, actor: str = "sistema") -> dict[str, str]:
    return {"step": step, "status": status, "detail": detail}


def _base_trace(session_id: str, channel: str, message: str) -> dict:
    receiver = "coordinador_expediente_penal"
    return {
        "trace_version": "4.0",
        "trace_id": _trace_id(session_id, message),
        "session_id": session_id,
        "timestamp": int(time.time() * 1000),
        "input_summary": _summarize_input(message),
        "channel": channel,
        "turn_index": 0,
        "spans": [],
        "received_by_agent": receiver,
        "sent_to_agent": "none",
        "skill_kan": _kan_for_agent(receiver),
        "skill_reason": "Orquestación inicial de consulta.",
        "route": "pending",
        "blocked": False,
        "selected_agent": "",
        "human_review_required": False,
        "completion": {
            "available": False,
            "provider": "openai-responses",
            "calls": [],
            "summary": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "note": "Se llena cuando hay ejecución LLM con API key.",
        },
        "actions": [],
        "steps": [
            _trace_step("Recibí su consulta", "done", "Consulta recibida por el asistente."),
            _trace_step(
                "Validé entrada",
                "done" if bool(message and message.strip()) else "blocked",
                "La consulta tiene formato válido." if bool(message and message.strip()) else "La consulta llegó vacía.",
            ),
        ],
    }


def _append_action(trace: dict, action_type: str, status: str, actor: str, detail: str) -> None:
    trace["actions"].append(
        {
            "type": action_type,
            "status": status,
            "actor": actor,
            "detail": detail,
            "at_ms": int(time.time() * 1000),
        }
    )


def _finalize_trace(trace: dict, text: str) -> dict:
    has_disclaimer = "Borrador informativo" in text
    span_count = len(trace.get("spans") or [])
    step_count = len(trace.get("steps") or [])
    trace["span_count"] = span_count
    trace["step_count"] = step_count
    trace.setdefault("spans", []).append(
        {
            "name": "Traza: cierre de turno",
            "kind": "session",
            "status": "done",
            "detail": f"Turno {trace.get('turn_index', 0)} finalizado con {span_count} spans y {step_count} pasos.",
            "at_ms": int(time.time() * 1000),
        }
    )
    _append_action(
        trace,
        action_type="output_guardrail",
        status="done",
        actor="guardrails",
        detail="Se aplicó salida con aviso legal para revisión humana."
        if has_disclaimer
        else "Se generó salida sin aviso legal detectado.",
    )
    trace["steps"].append(
        _trace_step(
            "Apliqué aviso legal",
            "done",
            "Respuesta marcada como borrador informativo para revisión humana."
            if has_disclaimer
            else "Respuesta generada sin aviso legal detectado.",
        )
    )
    return trace


def _fallback_response(message: str) -> str:
    """Respuesta offline determinista cuando no hay OPENAI_API_KEY."""
    dest = infer_destination_agent(message)
    bodies = {
        "evaluador_derechos_fundamentales_tutela": (
            "Puedo evaluar la procedencia preliminar de tutela en un contexto penal. "
            "Compárteme accionante, accionado, hechos, derecho fundamental vulnerado y por qué "
            "las vías ordinarias no son suficientes en este caso."
        ),
        "gestor_seguimiento_procesal_penal": (
            "Puedo estructurar el seguimiento procesal penal: estado del radicado, últimas actuaciones, "
            "audiencias próximas y alertas operativas de términos."
        ),
        "preparador_estrategico_audiencias_penales": (
            "Puedo preparar la audiencia penal: objetivo de intervención, guion, solicitudes, "
            "preguntas clave y riesgos tácticos para representación de víctimas."
        ),
        "gestor_evidencia_y_soporte_probatorio": (
            "Puedo construir el plan probatorio: inventario de evidencia, matriz hecho-prueba, "
            "brechas y plan de recaudo sin comprometer cadena de custodia."
        ),
        "analista_tipicidad_y_responsabilidad_penal": (
            "Puedo hacer análisis preliminar de tipicidad y responsabilidad penal. "
            "Compárteme hechos cronológicos, actores y soportes para mapear elementos del tipo."
        ),
        "analista_ruta_procesal_ley906": (
            "Puedo analizar ruta procesal Ley 906: etapa, actuaciones posibles para la víctima, "
            "riesgos procesales y próximos pasos."
        ),
        "analista_representacion_victimas": (
            "Puedo estructurar la estrategia de representación de víctimas: intereses, derechos, "
            "riesgos de revictimización y enfoque diferencial."
        ),
        "analista_cronologia_hechos_penales": (
            "Puedo ordenar la cronología penal del caso, identificar contradicciones y vacíos de información "
            "para fortalecer el análisis posterior."
        ),
        "redactor_documentos_juridicos_penales": (
            "Puedo redactar un borrador penal revisable (memorial, solicitud, recurso preliminar, "
            "derecho de petición o pieza de tutela preliminar). Comparte radicado, hechos y petición."
        ),
        "analista_calidad_juridica": (
            "Puedo revisar calidad jurídica: soporte fáctico, citas, coherencia estratégica "
            "y riesgos de confidencialidad o revictimización antes de salida externa."
        ),
    }
    if is_non_penal_scope_request(message):
        body = (
            "Esta solicitud está fuera de alcance penal-víctimas. Solo atiendo representación de víctimas "
            "en contexto penal colombiano. Si existe componente penal, compárteme hechos, etapa Ley 906 "
            "y objetivo procesal para continuar."
        )
    elif any(
        w in (message or "").lower()
        for w in ("perfil", "experiencia", "quien eres", "quién eres")
    ):
        body = (
            "Soy el Gerente del Caso Penal del despacho: tu único interlocutor. "
            "Cuando hace falta, consulto al equipo interno (cronología, tipicidad, ruta Ley 906, "
            "evidencia, audiencias, redacción, seguimiento, tutela y calidad) y te entrego una sola "
            "voz de despacho para tu revisión."
        )
    else:
        body = bodies.get(
            dest,
            (
                "Como Gerente del Caso Penal puedo apoyar estrategia de víctimas de extremo a "
                "extremo: hechos, tipicidad, ruta 906, evidencia, audiencias, redacción, seguimiento y "
                "control de calidad. ¿Qué parte del caso necesitas trabajar primero?"
            ),
        )
    return apply_output_guardrails(body)


def _resolve_backoffice_agent(
    *,
    message: str,
    last_agent_name: str | None,
    trace: dict,
) -> str:
    """Especialista real (auditoría); el chat siempre habla como POC."""
    backoffice = trace.get("backoffice_agent")
    if isinstance(backoffice, str) and backoffice in SPECIALIST_AGENT_IDS:
        return backoffice
    if last_agent_name and last_agent_name in SPECIALIST_AGENT_IDS:
        return last_agent_name
    inferred = _infer_destination_agent(message)
    return inferred


def _ensure_poc_voice(text: str, *, last_agent_name: str | None, backoffice_agent: str) -> str:
    """Red de seguridad: si un handoff residual dejó voz de especialista, enmarca como POC."""
    if not last_agent_name or last_agent_name == POC_AGENT_ID:
        return text
    if last_agent_name in {"guardrail", "error", "fallback"}:
        return text
    if last_agent_name not in SPECIALIST_AGENT_IDS:
        return text
    label = agent_display_name(backoffice_agent or last_agent_name)
    stripped = (text or "").strip()
    if stripped.lower().startswith("como gerente del caso"):
        return text
    return (
        f"Como Gerente del Caso Penal, consolidé el trabajo del equipo interno "
        f"({label}):\n\n{stripped}"
    )


async def run_agent(
    message: str,
    channel: str = "web",
    session_id: str = "default",
    user_id: str = "",
) -> dict:
    """Ejecuta el coordinador penal con sesión multi-turno, validaciones encadenadas y traza enriquecida."""
    ok, err = check_input(message)
    settings = get_settings()
    trace = _base_trace(session_id=session_id, channel=channel, message=message)
    has_key = bool(settings.openai_api_key or os.environ.get("OPENAI_API_KEY"))
    uid = user_id or (session_id.split(":", 1)[-1] if ":" in session_id else session_id)

    chat = get_repository().get_chat_session(session_id)
    history = list(chat.messages) if chat else []
    from src.services.expediente_sync import sync_expediente_from_chat

    sync_expediente_from_chat(session_id, message, history, trace=trace)
    expediente = expediente_store.get_or_create(session_id)
    exp_resumen = expediente.resumen()
    requested_destination = _infer_destination_agent(message)
    triage = build_triage(
        message, expediente=expediente, destination=requested_destination
    )
    trace["triage_sistema"] = triage.model_dump()

    ok_pre, pre_err = run_pre_validations(
        message,
        history=history,
        expediente_resumen=exp_resumen,
        trace=trace,
        expediente=expediente,
        destination=requested_destination,
    )
    prior_traces = get_repository().list_session_traces(session_id, limit=40)
    attach_session_continuity(trace, history=history, session_id=session_id, prior_traces=prior_traces)
    if not ok or not ok_pre:
        trace["route"] = "guardrail_input" if not ok else "pipeline_pre"
        trace["blocked"] = True
        trace["skill_kan"] = "KAN-GUARDRAIL"
        trace["selected_agent"] = "guardrail"
        text = err or pre_err or "Entrada no válida."
        _finalize_trace(trace, text)
        get_repository().append_chat_message(
            session_id,
            channel=channel,
            user_id=uid,
            role="user",
            content=message,
            max_messages=settings.session_max_messages,
        )
        get_repository().append_chat_message(
            session_id,
            channel=channel,
            user_id=uid,
            role="assistant",
            content=text,
            max_messages=settings.session_max_messages,
        )
        return {"text": text, "agent": "guardrail", "pending_review": False, "trace": trace, "session_id": session_id}

    if requires_execution_plan(requested_destination):
        text = (
            "La verificación del expediente pasó. Por tratarse de una actuación de alto "
            "riesgo, continúe mediante el plan de ejecución y apruébelo antes de usar al "
            "equipo de redacción o tutela."
        )
        trace["route"] = "plan_required"
        trace["blocked"] = True
        trace["selected_agent"] = POC_AGENT_ID
        trace["sent_to_agent"] = "none"
        trace["human_review_required"] = True
        _finalize_trace(trace, text)
        return {
            "text": text,
            "agent": POC_AGENT_ID,
            "pending_review": True,
            "trace": trace,
            "session_id": session_id,
        }

    if not has_key:
        text = _fallback_response(message)
        pending_review = needs_human_review(text, channel, message)
        inferred_destination = requested_destination
        trace["route"] = "fallback_no_api_key"
        trace["blocked"] = False
        trace["selected_agent"] = "fallback"
        trace["sent_to_agent"] = inferred_destination
        trace["skill_kan"] = _kan_for_agent(inferred_destination)
        trace["skill_reason"] = "Clasificación heurística por intención en modo fallback."
        _append_action(
            trace,
            action_type="routing_decision",
            status="done",
            actor=trace["received_by_agent"],
            detail=f"Sin API key; se estimó destino {inferred_destination} ({trace['skill_kan']}).",
        )
        trace["steps"].append(
            _trace_step("Enruté al especialista", "done", f"Consulta estimada hacia {inferred_destination}.")
        )
        trace["steps"].append(
            _trace_step("Procesé la solicitud", "done", "Se usó modo de respaldo porque la integración IA no está disponible.")
        )
        text = run_post_validations(message, text, trace)
        trace["human_review_required"] = pending_review
        trace["completion"]["note"] = "Sin OPENAI_API_KEY; no hubo completion real."
        draft_id = None
        if pending_review:
            draft_id = _maybe_create_draft(
                session_id=session_id,
                message=message,
                text=text,
                destination_agent=inferred_destination,
                trace=trace,
            )
        hr_status, hr_detail = _human_review_trace(pending_review, draft_id)
        _append_action(
            trace,
            action_type="human_review",
            status=hr_status,
            actor="guardrails",
            detail=hr_detail,
        )
        trace["steps"].append(
            _trace_step("Revisión humana", hr_status, hr_detail)
        )
        _finalize_trace(trace, text)
        get_repository().append_chat_message(
            session_id, channel=channel, user_id=uid, role="user", content=message,
            max_messages=settings.session_max_messages,
        )
        get_repository().append_chat_message(
            session_id, channel=channel, user_id=uid, role="assistant", content=text,
            max_messages=settings.session_max_messages,
        )
        return {
            "text": text,
            "agent": POC_AGENT_ID,
            "pending_review": pending_review,
            "draft_id": draft_id,
            "session_id": session_id,
            "trace": trace,
        }

    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

    destination_agent = trace["received_by_agent"]
    trace_hooks = _TraceRunHooks(trace)
    agent_session = RepositoryAgentSession(session_id, channel=channel, user_id=uid)
    from src.agents.context_security import wrap_untrusted_context

    context_block = format_triage_sistema(triage) + "\n"
    trivial = is_trivial_consultation(
        message, destination=requested_destination
    )
    if triage.escalar_humano and not trivial:
        from src.agents.urgency import UrgencyResult

        notice = format_escalation_notice(
            UrgencyResult(
                nivel_urgencia=triage.nivel_urgencia,
                motivos=list(triage.motivos_urgencia),
                accion_inmediata_sugerida=triage.accion_inmediata_urgencia,
                escalar_humano=True,
            )
        )
        context_block += notice + "\n\n"
        trace.setdefault("spans", []).append(
            {
                "name": "Gerencia: escalamiento por urgencia",
                "kind": "guardrail",
                "status": "pending",
                "detail": (
                    f"nivel={triage.nivel_urgencia}; "
                    f"motivos={'; '.join(triage.motivos_urgencia) or 'n/a'}"
                ),
                "at_ms": int(time.time() * 1000),
            }
        )
        trace["urgencia_escalamiento"] = {
            "nivel": triage.nivel_urgencia,
            "escalar_humano": True,
            "notice": notice,
        }
    if exp_resumen and "sin datos" not in exp_resumen.lower():
        exp_context, exp_flags = wrap_untrusted_context(
            exp_resumen,
            label="EXPEDIENTE DEL CASO",
        )
        context_block += f"[Expediente del caso]\n{exp_context}\n\n"
        if exp_flags:
            trace["context_security_flags"] = exp_flags

    # Prefetch RAG una sola vez; la tool buscar_en_conocimiento solo se expone
    # si el prefetch falló o quedó degradado (evita RAG doble).
    rag_prefetch_ok = False
    try:
        from src.services.rag import buscar, contexto_para_prompt

        rag_chunks = buscar(message, incluir_kb=True, k=4)
        rag_text = contexto_para_prompt(rag_chunks)
        if rag_text and "No se encontraron" not in rag_text:
            from src.services.rag import last_embed_used_local_fallback

            degraded = last_embed_used_local_fallback()
            if degraded:
                detail = (
                    "Recuperación descartada: embeddings locales no semánticos. "
                    "El turno continúa sin grounding RAG."
                )
                logger.warning("RAG prefetch con embedding local fallback session=%s", session_id)
                trace["grounding_degraded"] = True
                trace["rag_chunks_count"] = 0
            else:
                rag_context, rag_flags = wrap_untrusted_context(
                    rag_text,
                    label="BASE DE CONOCIMIENTO",
                )
                context_block += (
                    "[Base de conocimiento — fragmentos relevantes]\n"
                    f"{rag_context}\n\n"
                )
                detail = f"{len(rag_chunks)} fragmento(s) inyectados al contexto del turno."
                trace["rag_chunks_count"] = len(rag_chunks)
                rag_prefetch_ok = True
                if rag_flags:
                    existing_flags = list(trace.get("context_security_flags") or [])
                    trace["context_security_flags"] = sorted(
                        set(existing_flags + rag_flags)
                    )
            trace.setdefault("spans", []).append(
                {
                    "name": "RAG: recuperación KB",
                    "kind": "context",
                    "status": "pending" if degraded else "done",
                    "detail": detail,
                    "at_ms": int(time.time() * 1000),
                }
            )
            trace["rag_embed_fallback"] = degraded
    except Exception:
        logger.exception("RAG prefetch falló")
        trace.setdefault("spans", []).append(
            {
                "name": "RAG: recuperación KB",
                "kind": "context",
                "status": "pending",
                "detail": "No se pudo recuperar contexto de la KB en este turno.",
                "at_ms": int(time.time() * 1000),
            }
        )

    # Defensa estructural: el chat no recibe tools de redacción/tutela. Aunque
    # falle el clasificador, solo un plan aprobado puede instanciar esos agentes.
    # G1: superficie dinámica (focus + vecinos), sin lecturas MD completas,
    # sin tool KB si el prefetch ya inyectó fragmentos.
    chat_specialist_pool = SPECIALIST_AGENT_IDS - frozenset(
        {
            "redactor_documentos_juridicos_penales",
            "evaluador_derechos_fundamentales_tutela",
        }
    )
    enabled_specialists = enabled_specialists_for_focus(
        requested_destination, chat_specialist_pool
    )
    include_kb_search = not rag_prefetch_ok
    # Chat: alto riesgo va por plan HITL, no por interruptions del SDK
    # (include_high_risk_tools=False ⇒ no hay tools con needs_approval aquí).
    orchestrator = build_orchestrator(
        require_tool_approval=False,
        include_high_risk_tools=False,
        focus_agent_id=requested_destination,
        include_kb_search_tool=include_kb_search,
        include_full_read_tools=False,
        include_list_areas_tool=False,
        slim_instructions=True,
        use_cache=True,
    )
    instr_stats = getattr(orchestrator, "instruction_stats", None) or {
        "chars": len(orchestrator.instructions or ""),
        "approx_tokens": max(1, len(orchestrator.instructions or "") // 4),
    }
    trace["gerente_tool_surface"] = {
        "focus": requested_destination,
        "enabled_specialists": sorted(enabled_specialists),
        "kb_search_tool": include_kb_search,
        "full_read_tools": False,
        "list_areas_tool": False,
        "rag_prefetch_ok": rag_prefetch_ok,
        "max_turns": settings.agent_max_turns,
        "nested_max_turns": settings.agent_nested_max_turns,
        "instruction_chars": instr_stats.get("chars"),
        "slim_instructions": True,
    }
    agent_input = (
        f"{context_block}[Consulta del despacho]\n{message}"
        if context_block
        else message
    )
    trace.setdefault("spans", []).append(
        {
            "name": "runner:inicio",
            "kind": "agent",
            "status": "in_progress",
            "detail": f"Runner.run con hasta {settings.agent_max_turns} turnos internos y sesión persistida.",
            "at_ms": int(time.time() * 1000),
        }
    )
    run_config = RunConfig(
        workflow_name="firma-juridica",
        group_id=session_id,
        trace_metadata={
            "session_id": session_id,
            "channel": channel,
            "turn_index": str(trace.get("turn_index", 0)),
        },
    )
    try:
        from agents.exceptions import (
            InputGuardrailTripwireTriggered,
            OutputGuardrailTripwireTriggered,
        )

        result = None
        original_model = orchestrator.model

        async def _on_retry(attempt: int, exc: BaseException, delay: float) -> None:
            fallback_model = (settings.openai_model_fallback or "").strip()
            if fallback_model:
                orchestrator.model = fallback_model
            trace.setdefault("spans", []).append(
                {
                    "name": "runner:reintento",
                    "kind": "resilience",
                    "status": "pending",
                    "detail": (
                        f"Intento {attempt + 1} falló ({type(exc).__name__}); "
                        f"reintento en {delay:.2f}s"
                        + (f" con {fallback_model}." if fallback_model else ".")
                    ),
                    "at_ms": int(time.time() * 1000),
                }
            )

        try:
            with bind_active_session(session_id):
                result = await run_with_retries(
                    lambda: Runner.run(
                        orchestrator,
                        agent_input,
                        session=agent_session,
                        max_turns=settings.agent_max_turns,
                        hooks=trace_hooks,
                        run_config=run_config,
                    ),
                    max_retries=settings.agent_max_retries,
                    timeout_seconds=settings.agent_run_timeout_seconds,
                    on_retry=_on_retry,
                    non_retryable=(
                        InputGuardrailTripwireTriggered,
                        OutputGuardrailTripwireTriggered,
                        AgentBudgetExceeded,
                    ),
                )
        finally:
            # No contaminar el Agent cacheado con el modelo de fallback.
            orchestrator.model = original_model
        if result is None:  # pragma: no cover - defensa de invariantes
            raise RuntimeError("El runner terminó sin resultado.")
        if agent_session.last_compaction:
            trace["session_compaction"] = dict(agent_session.last_compaction)
        trace.setdefault("spans", []).append(
            {
                "name": "runner:fin",
                "kind": "agent",
                "status": "done",
                "detail": f"Ejecución completada; {len(getattr(result, 'new_items', []) or [])} eventos nuevos.",
                "at_ms": int(time.time() * 1000),
            }
        )
        last_agent_name = getattr(getattr(result, "last_agent", None), "name", None)
        backoffice_agent = _resolve_backoffice_agent(
            message=message,
            last_agent_name=last_agent_name,
            trace=trace,
        )
        raw_out = result.final_output or ""
        if raw_out and not isinstance(raw_out, str):
            raw_out = str(raw_out)

        interruptions = list(getattr(result, "interruptions", []) or [])
        if interruptions:
            tool_names: list[str] = []
            for item in interruptions:
                name = getattr(item, "tool_name", None) or getattr(
                    getattr(item, "raw_item", None), "name", None
                )
                if not name:
                    # ToolApprovalItem: try common accessors
                    try:
                        name = item.raw_item.get("name")  # type: ignore[union-attr]
                    except Exception:
                        name = None
                tool_names.append(str(name or "herramienta_critica"))
            tools_label = ", ".join(dict.fromkeys(tool_names))
            text = apply_output_guardrails(
                "Para continuar necesito su aprobación humana: el despacho está a punto de "
                f"consultar al equipo de alto riesgo ({tools_label}). "
                "Apruebe el plan de ejecución en el chat (web) o confirme con EJECUTAR en Slack "
                "para autorizar redacción o evaluación de tutela.",
                channel,
            )
            text = _ensure_poc_voice(
                text,
                last_agent_name=POC_AGENT_ID,
                backoffice_agent=POC_AGENT_ID,
            )
            trace["route"] = "tool_approval"
            trace["blocked"] = True
            trace["selected_agent"] = POC_AGENT_ID
            trace["sent_to_agent"] = "none"
            trace["skill_kan"] = "KAN-HITL-TOOL"
            trace["skill_reason"] = (
                f"POC pausó por needs_approval en tool(s): {tools_label}."
            )
            trace["pending_tool_approvals"] = tool_names
            _append_action(
                trace,
                action_type="tool_approval",
                status="blocked",
                actor=POC_AGENT_ID,
                detail=f"Interrupción HITL: {tools_label}",
            )
            trace["steps"].append(
                _trace_step(
                    "Aprobación de herramienta",
                    "blocked",
                    f"Se requiere aprobación para: {tools_label}.",
                )
            )
            trace["human_review_required"] = True
            _finalize_trace(trace, text)
            return {
                "text": text,
                "agent": POC_AGENT_ID,
                "pending_review": True,
                "session_id": session_id,
                "trace": trace,
            }

        text = apply_output_guardrails(raw_out, channel)
        text = _ensure_poc_voice(
            text,
            last_agent_name=last_agent_name,
            backoffice_agent=backoffice_agent,
        )
        text = run_post_validations(message, text, trace)
        destination_agent = backoffice_agent
        trace["sent_to_agent"] = destination_agent
        trace["skill_kan"] = _kan_for_agent(destination_agent)
        trace["skill_reason"] = (
            f"POC consultó backoffice ({destination_agent}) y sintetizó respuesta de despacho."
            if destination_agent != POC_AGENT_ID
            else "POC atendió la consulta directamente sin tool de especialista."
        )
        _append_action(
            trace,
            action_type="routing_decision",
            status="done",
            actor=POC_AGENT_ID,
            detail=(
                f"Backoffice {destination_agent} con skill {trace['skill_kan']}; "
                f"voz de cara al abogado: {POC_AGENT_ID}."
            ),
        )
        for item in getattr(result, "new_items", []) or []:
            item_type = item.__class__.__name__
            if item_type in {"HandoffCallItem", "HandoffOutputItem", "ToolCallItem", "ToolCallOutputItem"}:
                _append_action(
                    trace,
                    action_type="runtime_event",
                    status="done",
                    actor=item_type,
                    detail=f"Evento de ejecución detectado: {item_type}.",
                )
        calls = trace["completion"]["calls"]
        if calls:
            trace["completion"]["summary"] = _completion_summary(calls)
            trace["completion"]["available"] = True
            _append_action(
                trace,
                action_type="completion_summary",
                status="done",
                actor="llm",
                detail=(
                    f"Se ejecutaron {trace['completion']['summary']['calls']} completion(s), "
                    f"{trace['completion']['summary']['total_tokens']} tokens totales."
                ),
            )
        else:
            trace["completion"]["note"] = "No se recibieron eventos de completion en hooks."
    except AgentBudgetExceeded as exc:
        logger.warning("Presupuesto de agente excedido channel=%s: %s", channel, exc)
        text = apply_output_guardrails(
            "Detuve la ejecución porque alcanzó el presupuesto operativo del turno. "
            "Divida la consulta o continúe mediante un plan por pasos.",
            channel,
        )
        trace["route"] = "budget_exceeded"
        trace["blocked"] = True
        trace["selected_agent"] = "guardrail"
        trace["sent_to_agent"] = "none"
        trace["skill_kan"] = "KAN-GUARDRAIL"
        trace["skill_reason"] = "Watchdog de presupuesto de tokens."
        trace["human_review_required"] = False
        _append_action(
            trace,
            action_type="cost_budget",
            status="blocked",
            actor="watchdog",
            detail=str(exc),
        )
        _finalize_trace(trace, text)
        return {
            "text": text,
            "agent": "guardrail",
            "pending_review": False,
            "session_id": session_id,
            "trace": trace,
        }
    except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered) as exc:
        logger.warning("Guardrail tripwire channel=%s: %s", channel, exc)
        exc_name = type(exc).__name__
        if "Output" in exc_name:
            msg = (
                "No puedo entregar esa salida: activó un límite de seguridad del despacho "
                "(posible dato sensible o respuesta vacía). Reformule sin PII innecesaria "
                "o solicite el dato por canal seguro."
            )
        else:
            msg = (
                "No puedo procesar esa consulta en el alcance del despacho penal-víctimas. "
                "Reformule con el componente penal o de representación de víctimas "
                "(sin intentos de override de instrucciones)."
            )
        text = apply_output_guardrails(msg, channel)
        trace["route"] = "sdk_guardrail"
        trace["blocked"] = True
        trace["selected_agent"] = "guardrail"
        trace["sent_to_agent"] = "none"
        trace["skill_kan"] = "KAN-GUARDRAIL"
        trace["skill_reason"] = "Tripwire de guardrail nativo del Agents SDK."
        trace["completion"]["note"] = "Ejecución detenida por guardrail."
        _append_action(
            trace,
            action_type="sdk_guardrail",
            status="blocked",
            actor="poc_guardrail",
            detail=str(exc),
        )
        trace["steps"].append(
            _trace_step("Guardrail SDK", "blocked", "La consulta o salida activó un límite del despacho.")
        )
        trace["human_review_required"] = False
        _finalize_trace(trace, text)
        return {
            "text": text,
            "agent": "guardrail",
            "pending_review": False,
            "session_id": session_id,
            "trace": trace,
        }
    except Exception:
        logger.exception("Runner.run falló para channel=%s", channel)
        text = apply_output_guardrails(
            "No pude procesar la consulta en este momento. Intente de nuevo en unos segundos.",
            channel,
        )
        trace["route"] = "error"
        trace["blocked"] = False
        trace["selected_agent"] = "error"
        trace["sent_to_agent"] = "none"
        trace["skill_kan"] = "KAN-ERROR"
        trace["skill_reason"] = "Falla técnica durante ejecución de agentes."
        trace["completion"]["note"] = "Ejecución interrumpida por error interno."
        _append_action(
            trace,
            action_type="routing_decision",
            status="blocked",
            actor=trace["received_by_agent"],
            detail="No se pudo completar enrutamiento por error interno.",
        )
        trace["steps"].append(
            _trace_step("Procesé la solicitud", "blocked", "Ocurrió un error interno al procesar la consulta.")
        )
        trace["human_review_required"] = False
        trace["steps"].append(
            _trace_step("Revisión humana", "done", "Se devolvió mensaje de error controlado.")
        )
        _finalize_trace(trace, text)
        return {"text": text, "agent": "error", "pending_review": False, "session_id": session_id, "trace": trace}

    pending_review = needs_human_review(text, channel, message)
    trace["route"] = "orchestrator"
    trace["blocked"] = False
    trace["selected_agent"] = destination_agent
    if destination_agent != POC_AGENT_ID:
        trace["steps"].append(
            _trace_step(
                "Consulté al equipo interno",
                "done",
                f"Backoffice: {destination_agent}. Respuesta al abogado en voz del POC.",
            )
        )
    else:
        trace["steps"].append(
            _trace_step("Atendí como coordinador", "done", "Consulta resuelta por el POC sin especialista.")
        )
    trace["human_review_required"] = pending_review
    draft_id = None
    if pending_review:
        draft_id = _maybe_create_draft(
            session_id=session_id,
            message=message,
            text=text,
            destination_agent=destination_agent,
            trace=trace,
        )
    hr_status, hr_detail = _human_review_trace(pending_review, draft_id)
    _append_action(
        trace,
        action_type="human_review",
        status=hr_status,
        actor="guardrails",
        detail=hr_detail,
    )
    trace["steps"].append(
        _trace_step("Revisión humana", hr_status, hr_detail)
    )
    _finalize_trace(trace, text)
    reconcile_turn_messages(session_id, user_text=message, assistant_text=text)
    return {
        "text": text,
        "agent": POC_AGENT_ID,
        "pending_review": pending_review,
        "draft_id": draft_id,
        "session_id": session_id,
        "trace": trace,
    }
