"""Supresión ARCO de datos del titular (chat web / sesión del despacho)."""

from __future__ import annotations

import logging

from src.agents.plan_patterns import clear_session_pattern
from src.storage import get_repository

logger = logging.getLogger(__name__)


def erase_web_subject(user_id: str, *, channel: str = "web") -> dict:
    """Borra datos operativos asociados a un sujeto web (Ley 1581 — supresión).

    Conserva registros de consentimiento e access logs (trazabilidad del tratamiento).
    El historial archivado del portal de auditoría no se toca desde este flujo.
    """
    uid = (user_id or "").strip()
    if not uid:
        return {"ok": False, "detail": "user_id vacío"}
    session_id = f"{channel}:{uid}"
    repo = get_repository()

    cleared_traces = repo.clear_session_traces(session_id)
    deleted_drafts = repo.delete_drafts_for_session(session_id)
    deleted_plans = repo.delete_execution_plans_for_user(uid)
    deleted_exp = repo.delete_expediente(session_id)
    deleted_chat = repo.delete_chat_session(session_id)
    # Si solo había mensajes (sin hard-delete previo), reset vacío por si quedó fila
    if not deleted_chat:
        repo.reset_chat_session(session_id)
    clear_session_pattern(session_id)

    result = {
        "ok": True,
        "session_id": session_id,
        "cleared_traces": cleared_traces,
        "deleted_drafts": deleted_drafts,
        "deleted_execution_plans": deleted_plans,
        "deleted_expediente": deleted_exp,
        "deleted_chat_session": deleted_chat,
        "retained": ["compliance_consent", "audit_portal_access_log"],
    }
    logger.info(
        "ARCO erase web subject=%s traces=%s drafts=%s plans=%s",
        uid,
        cleared_traces,
        deleted_drafts,
        deleted_plans,
    )
    return result
