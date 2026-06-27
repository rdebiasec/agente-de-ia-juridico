"""Ejecutor de agentes con fallback sin API key."""

from __future__ import annotations

import json
import logging
import os
import time
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
        return {"text": err or "Entrada no válida.", "agent": "guardrail", "pending_review": False}

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
        return {
            "text": text,
            "agent": f"orquestador_fase{settings.active_phase}",
            "pending_review": False,
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
        return {
            "text": text,
            "agent": "fallback",
            "pending_review": needs_human_review(text, channel, message),
        }

    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

    orchestrator = build_orchestrator()
    try:
        result = await Runner.run(orchestrator, message)
        text = apply_output_guardrails(result.final_output or "", channel)
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
        return {
            "text": text,
            "agent": "error",
            "pending_review": False,
            "session_id": session_id,
        }

    return {
        "text": text,
        "agent": f"orquestador_fase{settings.active_phase}",
        "pending_review": needs_human_review(text, channel, message),
        "session_id": session_id,
    }
