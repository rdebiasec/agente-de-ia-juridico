"""BOLA — acceso a borradores HITL atado al subject_id de la sesión web."""

from __future__ import annotations

from fastapi import HTTPException

from src.auth.gate import auth_enabled
from src.config import Settings
from src.storage.models import Draft


def web_session_id_for_subject(subject_id: str, *, channel: str = "web") -> str:
    return f"{channel}:{subject_id}"


def draft_owned_by_subject(draft: Draft, subject_id: str) -> bool:
    """True si el borrador pertenece a la sesión web del subject autenticado."""
    owned = web_session_id_for_subject(subject_id)
    return (draft.session_id or "") == owned


def require_draft_for_subject(
    draft: Draft | None,
    subject_id: str,
    *,
    settings: Settings,
) -> Draft:
    """404 si no existe; 403 si auth ON y no es del subject."""
    if draft is None:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")
    if auth_enabled(settings.site_password) and not draft_owned_by_subject(draft, subject_id):
        raise HTTPException(status_code=403, detail="No autorizado para este borrador.")
    return draft


def resolve_list_session_id(
    *,
    subject_id: str,
    settings: Settings,
    requested_session_id: str | None = None,
) -> str | None:
    """Con auth ON siempre filtra por web:{subject}. Sin auth, respeta query opcional."""
    if auth_enabled(settings.site_password):
        owned = web_session_id_for_subject(subject_id)
        if requested_session_id and requested_session_id.strip() != owned:
            raise HTTPException(status_code=403, detail="No autorizado para esta sesión.")
        return owned
    raw = (requested_session_id or "").strip()
    return raw or None
