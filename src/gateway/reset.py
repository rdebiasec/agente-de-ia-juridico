"""Reinicio de conversación multi-turno (historial, trazas y expediente)."""

from __future__ import annotations

from src.agents.plan_patterns import clear_session_pattern
from src.storage import get_repository
from src.storage.models import Expediente


def reset_conversation(*, channel: str, user_id: str) -> dict:
    """Borra historial del agente, trazas y expediente para una sesión web."""
    session_id = f"{channel}:{user_id}"
    repo = get_repository()
    had_messages = repo.reset_chat_session(session_id)
    cleared_traces = repo.clear_session_traces(session_id)
    repo.save_expediente(Expediente(session_id=session_id))
    clear_session_pattern(session_id)
    return {
        "ok": True,
        "session_id": session_id,
        "cleared_messages": had_messages,
        "cleared_traces": cleared_traces,
    }
