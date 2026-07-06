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
from src.agents.orchestrator import build_orchestrator
from src.agents.pipeline import attach_session_continuity, run_post_validations, run_pre_validations
from src.config import get_settings
from src.gateway.agent_session import RepositoryAgentSession, reconcile_turn_messages
from src.gateway.expediente import expediente_store
from src.storage import get_repository

logger = logging.getLogger(__name__)

_TUTELA_RE = re.compile(r"\b(tutela|derecho fundamental|subsidiariedad|inmediatez)\b", re.IGNORECASE)
_SEGUIMIENTO_RE = re.compile(r"\b(seguimiento|radicado|actuaci[oó]n|vencimiento|t[eé]rmino|inactividad)\b", re.IGNORECASE)
_AUDIENCIA_RE = re.compile(r"\b(audiencia|interrogatorio|contrainterrogatorio|juicio|alegato)\b", re.IGNORECASE)
_EVIDENCIA_RE = re.compile(r"\b(evidencia|prueba|cadena de custodia|perit[oa]|testig)\b", re.IGNORECASE)
_TIPICIDAD_RE = re.compile(
    r"\b(tipicidad|tipo penal|autor[ií]a|participaci[oó]n|dolo|culpa|agravante|atenuante|conducta punible|delito)\b",
    re.IGNORECASE,
)
_RUTA906_RE = re.compile(
    r"\b(ley 906|imputaci[oó]n|acusaci[oó]n|preparatoria|control de garant[ií]as|etapa procesal|oportunidad procesal|fiscal[ií]a)\b",
    re.IGNORECASE,
)
_VICTIMAS_RE = re.compile(
    r"\b(v[ií]ctima|revictimizaci[oó]n|reparaci[oó]n integral|enfoque diferencial|derechos de la v[ií]ctima)\b",
    re.IGNORECASE,
)
_CRONOLOGIA_RE = re.compile(r"\b(cronolog[ií]a|linea de tiempo|hechos|narrativa factual|relato)\b", re.IGNORECASE)
_REDACCION_RE = re.compile(r"\b(memorial|solicitud|recurso|derecho de petici[oó]n|redact|escrito|borrador)\b", re.IGNORECASE)
_CALIDAD_RE = re.compile(r"\b(calidad|verificar|auditar|alucinaci[oó]n|coherencia|confidencialidad)\b", re.IGNORECASE)
_OUT_OF_SCOPE_RE = re.compile(
    r"\b(civil|familia|societari[oa]|comercial|laboral|consumidor|contractual|contrato|divorcio|custodia|alimentos|arrendamiento)\b",
    re.IGNORECASE,
)
_KNOWLEDGE_RE = re.compile(r"\b(ley 906|proceso penal|despacho penal|rutas penales)\b", re.IGNORECASE)
_PROFILE_RE = re.compile(r"\b(perfil|experiencia|qu[ií]en eres|quien eres)\b", re.IGNORECASE)

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
        return _truncate(dumped, limit=limit)
    except Exception:
        return _truncate(str(payload), limit=limit)


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

    async def on_tool_end(self, context: Any, agent: Any, tool: Any, result: object) -> None:
        tool_name = getattr(tool, "name", None) or type(tool).__name__
        self._span(
            f"tool:{tool_name}",
            "tool",
            "done",
            f"Resultado: {_truncate(_safe_json_preview(result, limit=200))}",
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
            "system_prompt": _truncate(system_prompt, limit=1400),
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


_PENAL_CONTEXT_PATTERNS = (
    _TUTELA_RE,
    _SEGUIMIENTO_RE,
    _AUDIENCIA_RE,
    _EVIDENCIA_RE,
    _TIPICIDAD_RE,
    _RUTA906_RE,
    _VICTIMAS_RE,
    _CRONOLOGIA_RE,
    _KNOWLEDGE_RE,
)


def _has_penal_context(message: str) -> bool:
    return any(pattern.search(message) for pattern in _PENAL_CONTEXT_PATTERNS)


def _is_non_penal_scope_request(message: str) -> bool:
    return bool(_OUT_OF_SCOPE_RE.search(message)) and not _has_penal_context(message)


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
        return None


def _infer_destination_agent(message: str) -> str:
    if _is_non_penal_scope_request(message):
        return "coordinador_expediente_penal"
    if _CALIDAD_RE.search(message):
        return "analista_calidad_juridica"
    if _TUTELA_RE.search(message):
        return "evaluador_derechos_fundamentales_tutela"
    if _SEGUIMIENTO_RE.search(message):
        return "gestor_seguimiento_procesal_penal"
    if _AUDIENCIA_RE.search(message):
        return "preparador_estrategico_audiencias_penales"
    if _EVIDENCIA_RE.search(message):
        return "gestor_evidencia_y_soporte_probatorio"
    if _TIPICIDAD_RE.search(message):
        return "analista_tipicidad_y_responsabilidad_penal"
    if _RUTA906_RE.search(message):
        return "analista_ruta_procesal_ley906"
    if _VICTIMAS_RE.search(message):
        return "analista_representacion_victimas"
    if _CRONOLOGIA_RE.search(message):
        return "analista_cronologia_hechos_penales"
    if _REDACCION_RE.search(message):
        return "redactor_documentos_juridicos_penales"
    if _PROFILE_RE.search(message):
        return "coordinador_expediente_penal"
    if _KNOWLEDGE_RE.search(message):
        return "analista_ruta_procesal_ley906"
    return "coordinador_expediente_penal"


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
    lower = message.lower()
    if _TUTELA_RE.search(lower):
        body = (
            "Puedo evaluar la procedencia preliminar de tutela en un contexto penal. "
            "Compárteme accionante, accionado, hechos, derecho fundamental vulnerado y por qué "
            "las vías ordinarias no son suficientes en este caso."
        )
    elif _SEGUIMIENTO_RE.search(lower):
        body = (
            "Puedo estructurar el seguimiento procesal penal: estado del radicado, últimas actuaciones, "
            "audiencias próximas y alertas operativas de términos."
        )
    elif _AUDIENCIA_RE.search(lower):
        body = (
            "Puedo preparar la audiencia penal: objetivo de intervención, guion, solicitudes, "
            "preguntas clave y riesgos tácticos para representación de víctimas."
        )
    elif _EVIDENCIA_RE.search(lower):
        body = (
            "Puedo construir el plan probatorio: inventario de evidencia, matriz hecho-prueba, "
            "brechas y plan de recaudo sin comprometer cadena de custodia."
        )
    elif _TIPICIDAD_RE.search(lower):
        body = (
            "Puedo hacer análisis preliminar de tipicidad y responsabilidad penal. "
            "Compárteme hechos cronológicos, actores y soportes para mapear elementos del tipo."
        )
    elif _RUTA906_RE.search(lower):
        body = (
            "Puedo analizar ruta procesal Ley 906: etapa, actuaciones posibles para la víctima, "
            "riesgos procesales y próximos pasos."
        )
    elif _VICTIMAS_RE.search(lower):
        body = (
            "Puedo estructurar la estrategia de representación de víctimas: intereses, derechos, "
            "riesgos de revictimización y enfoque diferencial."
        )
    elif _CRONOLOGIA_RE.search(lower):
        body = (
            "Puedo ordenar la cronología penal del caso, identificar contradicciones y vacíos de información "
            "para fortalecer el análisis posterior."
        )
    elif _is_non_penal_scope_request(lower):
        body = (
            "Esta solicitud está fuera de alcance penal-víctimas. Solo atiendo representación de víctimas "
            "en contexto penal colombiano. Si existe componente penal, compárteme hechos, etapa Ley 906 "
            "y objetivo procesal para continuar."
        )
    elif _REDACCION_RE.search(lower):
        body = (
            "Puedo redactar un borrador penal revisable (memorial, solicitud, recurso preliminar, "
            "derecho de petición o pieza de tutela preliminar). Comparte radicado, hechos y petición."
        )
    elif any(w in lower for w in ("perfil", "experiencia", "quien eres", "quién eres")):
        body = (
            "Soy la firma virtual penal-víctimas del despacho. Coordino especialistas en cronología, "
            "tipicidad, ruta Ley 906, evidencia, audiencias, redacción, seguimiento, tutela y calidad."
        )
    else:
        body = (
            "Puedo apoyar estrategia penal de víctimas de extremo a extremo: hechos, tipicidad, "
            "ruta 906, evidencia, audiencias, redacción, seguimiento y control de calidad. "
            "¿Qué parte del caso necesitas trabajar primero?"
        )
    return apply_output_guardrails(body)


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

    ok_pre, pre_err = run_pre_validations(
        message, history=history, expediente_resumen=exp_resumen, trace=trace
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
        return {"text": text, "agent": "guardrail", "pending_review": False, "trace": trace, "session_id": session_id}

    if not has_key:
        text = _fallback_response(message)
        pending_review = needs_human_review(text, channel, message)
        inferred_destination = _infer_destination_agent(message)
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
        _append_action(
            trace,
            action_type="human_review",
            status="pending" if pending_review else "done",
            actor="guardrails",
            detail="Pendiente de aprobación del abogado." if pending_review else "No requiere aprobación adicional para esta respuesta.",
        )
        trace["steps"].append(
            _trace_step(
                "Revisión humana",
                "pending" if pending_review else "done",
                "Pendiente de aprobación del abogado." if pending_review else "No requiere aprobación adicional para este tipo de salida.",
            )
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
        return {"text": text, "agent": "fallback", "pending_review": pending_review, "draft_id": draft_id, "session_id": session_id, "trace": trace}

    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

    orchestrator = build_orchestrator()
    destination_agent = trace["received_by_agent"]
    trace_hooks = _TraceRunHooks(trace)
    agent_session = RepositoryAgentSession(session_id, channel=channel, user_id=uid)
    context_block = ""
    if exp_resumen and "sin datos" not in exp_resumen.lower():
        context_block = f"[Expediente del caso]\n{exp_resumen}\n\n"
    try:
        from src.services.rag import buscar, contexto_para_prompt

        rag_chunks = buscar(message, incluir_kb=True, k=4)
        rag_text = contexto_para_prompt(rag_chunks)
        if rag_text and "No se encontraron" not in rag_text:
            context_block += f"[Base de conocimiento — fragmentos relevantes]\n{rag_text}\n\n"
            trace.setdefault("spans", []).append(
                {
                    "name": "RAG: recuperación KB",
                    "kind": "context",
                    "status": "done",
                    "detail": f"{len(rag_chunks)} fragmento(s) inyectados al contexto del turno.",
                    "at_ms": int(time.time() * 1000),
                }
            )
            trace["rag_chunks_count"] = len(rag_chunks)
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
    agent_input = f"{context_block}{message}" if context_block else message
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
        result = await Runner.run(
            orchestrator,
            agent_input,
            session=agent_session,
            max_turns=settings.agent_max_turns,
            hooks=trace_hooks,
            run_config=run_config,
        )
        trace.setdefault("spans", []).append(
            {
                "name": "runner:fin",
                "kind": "agent",
                "status": "done",
                "detail": f"Ejecución completada; {len(getattr(result, 'new_items', []) or [])} eventos nuevos.",
                "at_ms": int(time.time() * 1000),
            }
        )
        text = apply_output_guardrails(result.final_output or "", channel)
        text = run_post_validations(message, text, trace)
        destination_agent = getattr(getattr(result, "last_agent", None), "name", None) or trace["received_by_agent"]
        if destination_agent == trace["received_by_agent"]:
            destination_agent = _infer_destination_agent(message)
        trace["sent_to_agent"] = destination_agent
        trace["skill_kan"] = _kan_for_agent(destination_agent)
        trace["skill_reason"] = f"Handoff/resultado final del coordinador penal hacia {destination_agent}."
        _append_action(
            trace,
            action_type="routing_decision",
            status="done",
            actor=trace["received_by_agent"],
            detail=f"Consulta enviada a {destination_agent} con skill {trace['skill_kan']}.",
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
    trace["steps"].append(
        _trace_step("Enruté al especialista", "done", f"La consulta fue enrutada a {destination_agent}.")
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
    _append_action(
        trace,
        action_type="human_review",
        status="pending" if pending_review else "done",
        actor="guardrails",
        detail="Pendiente de aprobación del abogado." if pending_review else "No requiere aprobación adicional.",
    )
    trace["steps"].append(
        _trace_step(
            "Revisión humana",
            "pending" if pending_review else "done",
            "Pendiente de aprobación del abogado." if pending_review else "No requiere aprobación adicional.",
        )
    )
    _finalize_trace(trace, text)
    reconcile_turn_messages(session_id, user_text=message, assistant_text=text)
    return {
        "text": text,
        "agent": destination_agent,
        "pending_review": pending_review,
        "draft_id": draft_id,
        "session_id": session_id,
        "trace": trace,
    }
