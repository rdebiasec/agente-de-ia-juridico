"""Ejecutor de agentes con fallback sin API key."""

from __future__ import annotations

import logging
import os

from agents import Runner

logger = logging.getLogger(__name__)

from src.agents.guardrails import (
    apply_output_guardrails,
    check_input,
    check_phase_scope,
)
from src.agents.orchestrator import build_orchestrator
from src.config import get_settings


def _fallback_response(message: str) -> str:
    """Respuesta offline cuando no hay OPENAI_API_KEY."""
    from src.mcp.tools import _list_areas

    lower = message.lower()
    if any(w in lower for w in ("área", "area", "derecho", "cubre", "maneja")):
        body = _list_areas()
    elif any(w in lower for w in ("perfil", "experiencia", "quien eres", "quién eres")):
        body = (
            "Soy el asistente jurídico del despacho, con perfil equivalente a ~5 años "
            "de experiencia en derecho colombiano. Apoyo al abogado; no lo reemplazo."
        )
    else:
        scope = check_phase_scope(message)
        body = scope or (
            "En Fase 0 puedo orientar sobre el perfil del despacho y las áreas del "
            "derecho. ¿Sobre qué área desea información?"
        )
    return apply_output_guardrails(body)


async def run_agent(message: str, channel: str = "slack", session_id: str = "default") -> dict:
    """Ejecuta orquestador y aplica guardrails."""
    ok, err = check_input(message)
    if not ok:
        return {"text": err or "Entrada no válida.", "agent": "guardrail", "pending_review": False}

    scope_block = check_phase_scope(message)
    if scope_block and any(
        w in message.lower()
        for w in ("redact", "contrato", "tutela", "memorial", "demanda")
    ):
        text = apply_output_guardrails(scope_block, channel)
        return {"text": text, "agent": "orquestador_fase0", "pending_review": False}

    settings = get_settings()
    if not settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
        text = _fallback_response(message)
        return {
            "text": text,
            "agent": "fallback",
            "pending_review": channel == "whatsapp",
        }

    if settings.openai_api_key:
        os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)

    orchestrator = build_orchestrator()
    try:
        result = await Runner.run(orchestrator, message)
        text = apply_output_guardrails(result.final_output or "", channel)
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

    from src.agents.guardrails import needs_human_review

    return {
        "text": text,
        "agent": "orquestador_fase0",
        "pending_review": needs_human_review(text, channel),
        "session_id": session_id,
    }
