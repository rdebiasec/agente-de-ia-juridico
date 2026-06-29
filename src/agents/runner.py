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

from src.agents.guardrails import (
    apply_output_guardrails,
    check_input,
    needs_human_review,
)
from src.agents.orchestrator import build_orchestrator
from src.config import get_settings

logger = logging.getLogger(__name__)

_COMMUNICATION_RE = re.compile(r"\b(correo|mensaje|cliente|comunicaci[oó]n)\b", re.IGNORECASE)
_ANALYSIS_RE = re.compile(r"\b(riesgo|estrategia|teor[ií]a|prueba|debilidad)\b", re.IGNORECASE)
_TUTELA_RE = re.compile(r"\btutela\b", re.IGNORECASE)
_CONCEPT_RE = re.compile(r"\bconcepto\b", re.IGNORECASE)
_MEMORIAL_RE = re.compile(r"\b(memorial|radicado|impulso procesal|expediente|audiencia)\b", re.IGNORECASE)
_CIVIL_RE = re.compile(r"\b(demanda|contestaci[oó]n|excepci[oó]n|civil)\b", re.IGNORECASE)
_PENAL_RE = re.compile(r"\b(penal|fiscal[ií]a|imputaci[oó]n|interrogatorio)\b", re.IGNORECASE)
_DRAFTING_RE = re.compile(r"\b(contrato|redact|escrito|recurso|solicitud)\b", re.IGNORECASE)
_FOLLOWUP_RE = re.compile(r"\b(seguimiento|informe|radicaci[oó]n|estado)\b", re.IGNORECASE)
_KNOWLEDGE_RE = re.compile(r"\b([áa]rea|derecho|cubre|maneja)\b", re.IGNORECASE)
_PROFILE_RE = re.compile(r"\b(perfil|experiencia|qu[ií]en eres|quien eres)\b", re.IGNORECASE)

_AGENT_SKILL_MAP = {
    "orquestador": "KAN-4",
    "conocimiento_areas": "KAN-10",
    "intake": "KAN-11",
    "comunicacion_clientes": "KAN-11",
    "estratega": "KAN-12",
    "litigante_civil": "KAN-13",
    "litigante_penal": "KAN-13",
    "redaccion_documental": "KAN-13",
    "conceptos_juridicos": "KAN-17",
    "tutela_constitucional": "KAN-19",
    "dependiente_judicial": "KAN-14",
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

    async def on_llm_start(
        self,
        context: Any,
        agent: Any,
        system_prompt: str | None,
        input_items: list[Any],
    ) -> None:
        started_at_ms = int(time.time() * 1000)
        model_name = getattr(agent, "model", None) or get_settings().openai_model or "default"
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


def _kan_for_agent(agent_name: str | None) -> str:
    if not agent_name:
        return "KAN-N/A"
    return _AGENT_SKILL_MAP.get(agent_name, "KAN-N/A")


def _infer_destination_agent(message: str) -> str:
    if _TUTELA_RE.search(message):
        return "tutela_constitucional"
    if _FOLLOWUP_RE.search(message):
        return "dependiente_judicial"
    if _CONCEPT_RE.search(message):
        return "conceptos_juridicos"
    if _MEMORIAL_RE.search(message):
        return "redaccion_documental"
    if _PENAL_RE.search(message):
        return "litigante_penal"
    if _CIVIL_RE.search(message):
        return "litigante_civil"
    if _DRAFTING_RE.search(message):
        return "redaccion_documental"
    if _COMMUNICATION_RE.search(message):
        return "comunicacion_clientes"
    if _ANALYSIS_RE.search(message):
        return "estratega"
    if _PROFILE_RE.search(message):
        return "intake"
    if _KNOWLEDGE_RE.search(message):
        return "conocimiento_areas"
    return "conocimiento_areas"


def _trace_step(step: str, status: str, detail: str, actor: str = "sistema") -> dict[str, str]:
    return {"step": step, "status": status, "detail": detail}


def _base_trace(session_id: str, channel: str, message: str) -> dict:
    receiver = "orquestador"
    return {
        "trace_version": "3.0",
        "trace_id": _trace_id(session_id, message),
        "session_id": session_id,
        "timestamp": int(time.time() * 1000),
        "input_summary": _summarize_input(message),
        "channel": channel,
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
    from src.mcp.tools import _list_areas

    lower = message.lower()
    if _TUTELA_RE.search(lower):
        body = (
            "Puedo preparar un borrador de acción de tutela. Compárteme datos completos del "
            "accionante y accionado, el derecho fundamental presuntamente vulnerado y los hechos. "
            "Recuerda que el término de fallo (10 días hábiles) debe vigilarse."
        )
    elif _MEMORIAL_RE.search(lower):
        body = (
            "Puedo preparar un borrador de memorial. Indícame el tipo (solicitud de expediente, "
            "impulso procesal, solicitud de audiencia), el nombre del proceso, las partes y el radicado."
        )
    elif _CONCEPT_RE.search(lower):
        body = (
            "Puedo proyectar un concepto jurídico. Compárteme el nombre del cliente y el problema "
            "jurídico; fundamentaré con las normas de la base de conocimiento y daré una recomendación."
        )
    elif _FOLLOWUP_RE.search(lower):
        body = (
            "Puedo estructurar el seguimiento del proceso y un informe de novedades para el cliente. "
            "Compárteme el radicado, el estado actual y las últimas actuaciones."
        )
    elif _PENAL_RE.search(lower):
        body = (
            "Puedo apoyar el asunto penal según la etapa (Ley 906). Indícame la etapa procesal y la "
            "postura del despacho (defensa o representación de víctima)."
        )
    elif _CIVIL_RE.search(lower):
        body = (
            "Puedo apoyar el asunto civil según la etapa (CGP). Indícame si actuamos como demandante o "
            "demandado y la etapa actual del proceso."
        )
    elif any(w in lower for w in ("correo", "mensaje", "cliente")):
        body = (
            "Puedo proponer un borrador de comunicación profesional para el cliente. "
            "Compárteme destinatario, objetivo y tono deseado."
        )
    elif _ANALYSIS_RE.search(lower):
        body = (
            "Puedo hacer un análisis preliminar de riesgos y estrategia. "
            "Compárteme los hechos clave, el estado del caso y el objetivo del despacho."
        )
    elif _DRAFTING_RE.search(lower):
        body = (
            "Puedo redactar un borrador base (contrato, recurso, solicitud o excepción). "
            "Indica el tipo de documento, las partes, los hechos y la petición principal."
        )
    elif any(w in lower for w in ("área", "area", "derecho", "cubre", "maneja")):
        body = _list_areas()
    elif any(w in lower for w in ("perfil", "experiencia", "quien eres", "quién eres")):
        body = (
            "Soy el asistente jurídico del despacho, con perfil equivalente a ~5 años de experiencia "
            "en derecho colombiano (civil y penal). Apoyo al abogado; no lo reemplazo."
        )
    else:
        body = (
            "Puedo apoyar atención al cliente, análisis de riesgos y estrategia, redacción de contratos "
            "y escritos, conceptos, memoriales, tutelas y seguimiento de procesos. ¿Qué necesita?"
        )
    return apply_output_guardrails(body)


async def run_agent(message: str, channel: str = "web", session_id: str = "default") -> dict:
    """Ejecuta el orquestador de la firma y aplica guardrails."""
    ok, err = check_input(message)
    settings = get_settings()
    trace = _base_trace(session_id=session_id, channel=channel, message=message)
    has_key = bool(settings.openai_api_key or os.environ.get("OPENAI_API_KEY"))

    if not ok:
        trace["route"] = "guardrail_input"
        trace["blocked"] = True
        trace["skill_kan"] = "KAN-GUARDRAIL"
        trace["skill_reason"] = "Bloqueo temprano por validación de entrada."
        trace["selected_agent"] = "guardrail"
        _append_action(
            trace,
            action_type="input_validation",
            status="blocked",
            actor="guardrails",
            detail="La entrada no cumple validaciones mínimas.",
        )
        trace["steps"].append(
            _trace_step("Validé la entrada", "blocked", "La consulta no pasó validaciones básicas de entrada.")
        )
        trace["human_review_required"] = False
        text = err or "Entrada no válida."
        _finalize_trace(trace, text)
        return {"text": text, "agent": "guardrail", "pending_review": False, "trace": trace}

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
        trace["human_review_required"] = pending_review
        trace["completion"]["note"] = "Sin OPENAI_API_KEY; no hubo completion real."
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
        return {"text": text, "agent": "fallback", "pending_review": pending_review, "trace": trace}

    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

    orchestrator = build_orchestrator()
    destination_agent = trace["received_by_agent"]
    trace_hooks = _TraceRunHooks(trace)
    try:
        result = await Runner.run(orchestrator, message, hooks=trace_hooks)
        text = apply_output_guardrails(result.final_output or "", channel)
        destination_agent = getattr(getattr(result, "last_agent", None), "name", None) or trace["received_by_agent"]
        if destination_agent == trace["received_by_agent"]:
            destination_agent = _infer_destination_agent(message)
        trace["sent_to_agent"] = destination_agent
        trace["skill_kan"] = _kan_for_agent(destination_agent)
        trace["skill_reason"] = f"Handoff/resultado final del orquestador hacia {destination_agent}."
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
    return {
        "text": text,
        "agent": destination_agent,
        "pending_review": pending_review,
        "session_id": session_id,
        "trace": trace,
    }
