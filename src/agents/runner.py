"""Ejecutor de agentes con fallback sin API key."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from hashlib import sha1
from pathlib import Path

from agents import Runner

logger = logging.getLogger(__name__)
_DEBUG_LOG_83755E = Path(__file__).resolve().parents[2] / ".cursor" / "debug-83755e.log"


def _debug_log_83755e(run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    try:
        payload = {
            "sessionId": "83755e",
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        _DEBUG_LOG_83755E.parent.mkdir(parents=True, exist_ok=True)
        with _DEBUG_LOG_83755E.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass

from src.agents.guardrails import (
    apply_output_guardrails,
    check_input,
    check_phase_scope,
    needs_human_review,
)
from src.agents.orchestrator import build_orchestrator
from src.config import get_settings

_COMMUNICATION_RE = re.compile(r"\b(correo|mensaje|cliente|comunicaci[oó]n)\b", re.IGNORECASE)
_ANALYSIS_RE = re.compile(r"\b(riesgo|estrategia|teor[ií]a|prueba|debilidad)\b", re.IGNORECASE)
_DRAFTING_RE = re.compile(r"\b(contrato|redact|escrito|recurso|solicitud|excepci[oó]n)\b", re.IGNORECASE)
_KNOWLEDGE_RE = re.compile(r"\b([áa]rea|derecho|cubre|maneja)\b", re.IGNORECASE)
_PROFILE_RE = re.compile(r"\b(perfil|experiencia|qu[ií]en eres|quien eres)\b", re.IGNORECASE)

_AGENT_SKILL_MAP = {
    "orquestador_fase0": "KAN-5",
    "orquestador_fase1": "KAN-6",
    "perfil_abogado_colombia": "KAN-4",
    "conocimiento_areas_derecho": "KAN-4",
    "comunicacion_clientes_fase1": "KAN-11",
    "analisis_riesgo_fase1": "KAN-12",
    "redaccion_basica_fase1": "KAN-13",
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


def _kan_for_agent(agent_name: str | None) -> str:
    if not agent_name:
        return "KAN-N/A"
    return _AGENT_SKILL_MAP.get(agent_name, "KAN-N/A")


def _infer_destination_agent(message: str, active_phase: int) -> str:
    if active_phase <= 0:
        if _PROFILE_RE.search(message):
            return "perfil_abogado_colombia"
        if _KNOWLEDGE_RE.search(message):
            return "conocimiento_areas_derecho"
        return "conocimiento_areas_derecho"
    if _COMMUNICATION_RE.search(message):
        return "comunicacion_clientes_fase1"
    if _ANALYSIS_RE.search(message):
        return "analisis_riesgo_fase1"
    if _DRAFTING_RE.search(message):
        return "redaccion_basica_fase1"
    if _PROFILE_RE.search(message):
        return "perfil_abogado_colombia"
    if _KNOWLEDGE_RE.search(message):
        return "conocimiento_areas_derecho"
    return "conocimiento_areas_derecho"


def _trace_step(step: str, status: str, detail: str, actor: str = "sistema") -> dict[str, str]:
    return {"step": step, "status": status, "detail": detail}


def _base_trace(session_id: str, channel: str, active_phase: int, message: str) -> dict:
    receiver = f"orquestador_fase{active_phase}"
    return {
        "trace_version": "2.0",
        "trace_id": _trace_id(session_id, message),
        "session_id": session_id,
        "timestamp": int(time.time() * 1000),
        "input_summary": _summarize_input(message),
        "phase": active_phase,
        "channel": channel,
        "received_by_agent": receiver,
        "sent_to_agent": "none",
        "skill_kan": _kan_for_agent(receiver),
        "skill_reason": "Orquestación inicial de consulta.",
        "route": "pending",
        "blocked": False,
        "selected_agent": "",
        "human_review_required": False,
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
    _append_action(
        trace,
        action_type="output_guardrail",
        status="done",
        actor="guardrails",
        detail="Se aplicó salida con aviso legal para revisión humana."
        if "Borrador informativo" in text
        else "Se generó salida sin aviso legal detectado.",
    )
    trace["steps"].append(
        _trace_step(
            "Apliqué aviso legal",
            "done",
            "Respuesta marcada como borrador informativo para revisión humana."
            if "Borrador informativo" in text
            else "Respuesta generada sin aviso legal detectado.",
        )
    )
    return trace


def _fallback_response(message: str, active_phase: int) -> str:
    """Respuesta offline cuando no hay OPENAI_API_KEY."""
    from src.mcp.tools import _list_areas

    scope = check_phase_scope(message, active_phase=active_phase)
    if scope:
        return apply_output_guardrails(scope)

    lower = message.lower()
    if active_phase >= 1:
        if any(w in lower for w in ("correo", "mensaje", "cliente")):
            body = (
                "Puedo proponer un borrador de comunicación profesional para cliente. "
                "Compárteme destinatario, objetivo y tono deseado para redactarlo."
            )
            return apply_output_guardrails(body)
        if any(w in lower for w in ("riesgo", "estrategia", "teoría", "teoria", "prueba")):
            body = (
                "Puedo hacer un análisis preliminar de riesgos y estrategia. "
                "Compárteme hechos clave, estado del caso y objetivo del despacho."
            )
            return apply_output_guardrails(body)
        if any(w in lower for w in ("contrato", "escrito", "recurso", "solicitud", "excepción", "excepcion")):
            body = (
                "Puedo redactar un borrador base en Fase 1. "
                "Indica tipo de documento, partes involucradas, hechos y petición principal."
            )
            return apply_output_guardrails(body)

    if any(w in lower for w in ("área", "area", "derecho", "cubre", "maneja")):
        body = _list_areas()
    elif any(w in lower for w in ("perfil", "experiencia", "quien eres", "quién eres")):
        body = (
            "Soy el asistente jurídico del despacho, con perfil equivalente a ~5 años "
            "de experiencia en derecho colombiano. Apoyo al abogado; no lo reemplazo."
        )
    else:
        if active_phase >= 1:
            body = (
                "En Fase 1 puedo apoyar comunicación con clientes, análisis preliminar "
                "de riesgos y redacción básica. ¿Qué tipo de apoyo necesita?"
            )
        else:
            body = (
                "En Fase 0 puedo orientar sobre el perfil del despacho y las áreas del "
                "derecho. ¿Sobre qué área desea información?"
            )
    return apply_output_guardrails(body)


async def run_agent(message: str, channel: str = "slack", session_id: str = "default") -> dict:
    """Ejecuta orquestador y aplica guardrails."""
    ok, err = check_input(message)
    settings = get_settings()
    trace = _base_trace(session_id=session_id, channel=channel, active_phase=settings.active_phase, message=message)
    scope_block = check_phase_scope(message, active_phase=settings.active_phase)
    has_key = bool(settings.openai_api_key or os.environ.get("OPENAI_API_KEY"))
    # region agent log
    _debug_log_83755e(
        "pre-fix",
        "H1",
        "src/agents/runner.py:67",
        "run_agent_entry",
        {
            "channel": channel,
            "message_len": len(message or ""),
            "scope_block": bool(scope_block),
            "input_ok": bool(ok),
            "has_openai_key": has_key,
        },
    )
    # endregion
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
            _trace_step("Validé alcance de fase", "blocked", "La consulta no pasó validaciones básicas de entrada.")
        )
        trace["human_review_required"] = False
        text = err or "Entrada no válida."
        _finalize_trace(trace, text)
        return {"text": text, "agent": "guardrail", "pending_review": False, "trace": trace}

    if scope_block:
        text = apply_output_guardrails(scope_block, channel)
        # region agent log
        _debug_log_83755e(
            "pre-fix",
            "H1",
            "src/agents/runner.py:88",
            "scope_block_applied",
            {"channel": channel, "disclaimer_count": text.count("Borrador informativo")},
        )
        # endregion
        trace["route"] = "scope_block"
        trace["blocked"] = True
        trace["selected_agent"] = f"orquestador_fase{settings.active_phase}"
        trace["sent_to_agent"] = "none"
        trace["skill_kan"] = "KAN-OUT-OF-SCOPE"
        trace["skill_reason"] = "Consulta fuera del alcance de fase activa."
        _append_action(
            trace,
            action_type="scope_check",
            status="blocked",
            actor="guardrails",
            detail="Se bloqueó por pertenecer a capacidad de fase posterior.",
        )
        trace["steps"].append(
            _trace_step("Validé alcance de fase", "blocked", "La solicitud pertenece a una fase posterior y se bloqueó.")
        )
        trace["human_review_required"] = False
        _finalize_trace(trace, text)
        return {
            "text": text,
            "agent": f"orquestador_fase{settings.active_phase}",
            "pending_review": False,
            "trace": trace,
        }

    if not has_key:
        text = _fallback_response(message, settings.active_phase)
        # region agent log
        _debug_log_83755e(
            "pre-fix",
            "H5",
            "src/agents/runner.py:102",
            "fallback_path_selected",
            {"channel": channel, "disclaimer_count": text.count("Borrador informativo")},
        )
        # endregion
        pending_review = needs_human_review(text, channel, message)
        inferred_destination = _infer_destination_agent(message, settings.active_phase)
        trace["route"] = "fallback_no_api_key"
        trace["blocked"] = False
        trace["selected_agent"] = "fallback"
        trace["sent_to_agent"] = inferred_destination
        trace["skill_kan"] = _kan_for_agent(inferred_destination)
        trace["skill_reason"] = "Clasificación heurística por intención en modo fallback."
        _append_action(
            trace,
            action_type="scope_check",
            status="done",
            actor=trace["received_by_agent"],
            detail="Consulta dentro del alcance de fase activa.",
        )
        _append_action(
            trace,
            action_type="routing_decision",
            status="done",
            actor=trace["received_by_agent"],
            detail=f"Sin API key; se estimó destino {inferred_destination} ({trace['skill_kan']}).",
        )
        trace["steps"].append(
            _trace_step(
                "Validé alcance de fase",
                "done",
                "Consulta dentro del alcance de la fase activa.",
            )
        )
        trace["steps"].append(
            _trace_step(
                "Procesé la solicitud",
                "done",
                "Se usó modo de respaldo porque la integración IA no está disponible.",
            )
        )
        trace["human_review_required"] = pending_review
        _append_action(
            trace,
            action_type="human_review",
            status="pending" if pending_review else "done",
            actor="guardrails",
            detail="Pendiente de aprobación del abogado."
            if pending_review
            else "No requiere aprobación adicional para esta respuesta.",
        )
        trace["steps"].append(
            _trace_step(
                "Revisión humana",
                "pending" if pending_review else "done",
                "Pendiente de aprobación del abogado."
                if pending_review
                else "No requiere aprobación adicional para este tipo de salida.",
            )
        )
        _finalize_trace(trace, text)
        return {
            "text": text,
            "agent": "fallback",
            "pending_review": pending_review,
            "trace": trace,
        }

    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

    orchestrator = build_orchestrator()
    destination_agent = trace["received_by_agent"]
    try:
        result = await Runner.run(orchestrator, message)
        text = apply_output_guardrails(result.final_output or "", channel)
        destination_agent = getattr(getattr(result, "last_agent", None), "name", None) or trace["received_by_agent"]
        if destination_agent == trace["received_by_agent"]:
            destination_agent = _infer_destination_agent(message, settings.active_phase)
        trace["sent_to_agent"] = destination_agent
        trace["skill_kan"] = _kan_for_agent(destination_agent)
        trace["skill_reason"] = f"Handoff/resultado final del orquestador hacia {destination_agent}."
        _append_action(
            trace,
            action_type="scope_check",
            status="done",
            actor=trace["received_by_agent"],
            detail="Consulta permitida por guardrails de fase.",
        )
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
        # region agent log
        _debug_log_83755e(
            "pre-fix",
            "H3",
            "src/agents/runner.py:122",
            "runner_output_guardrailed",
            {"channel": channel, "disclaimer_count": text.count("Borrador informativo")},
        )
        # endregion
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
        _append_action(
            trace,
            action_type="routing_decision",
            status="blocked",
            actor=trace["received_by_agent"],
            detail="No se pudo completar enrutamiento por error interno.",
        )
        trace["steps"].append(
            _trace_step("Validé alcance de fase", "done", "Consulta dentro del alcance de la fase activa.")
        )
        trace["steps"].append(
            _trace_step("Procesé la solicitud", "blocked", "Ocurrió un error interno al procesar la consulta.")
        )
        trace["human_review_required"] = False
        trace["steps"].append(
            _trace_step("Revisión humana", "done", "Se devolvió mensaje de error controlado.")
        )
        _finalize_trace(trace, text)
        return {
            "text": text,
            "agent": "error",
            "pending_review": False,
            "session_id": session_id,
            "trace": trace,
        }

    pending_review = needs_human_review(text, channel, message)
    trace["route"] = "orchestrator"
    trace["blocked"] = False
    trace["selected_agent"] = destination_agent
    trace["steps"].append(
        _trace_step("Validé alcance de fase", "done", "Consulta dentro del alcance de la fase activa.")
    )
    trace["steps"].append(
        _trace_step(
            "Enruté al especialista",
            "done",
            "La consulta fue enrutada al flujo de agentes de Fase 1.",
        )
    )
    trace["human_review_required"] = pending_review
    _append_action(
        trace,
        action_type="human_review",
        status="pending" if pending_review else "done",
        actor="guardrails",
        detail="Pendiente de aprobación del abogado."
        if pending_review
        else "No requiere aprobación adicional.",
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
        "agent": f"orquestador_fase{settings.active_phase}",
        "pending_review": pending_review,
        "session_id": session_id,
        "trace": trace,
    }
