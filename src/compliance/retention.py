"""Purga automática según ventanas declaradas en policy (Ley 1581 — principio de temporalidad)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from src.compliance.arco import erase_web_subject
from src.compliance.policy import DATA_CONTROLLER
from src.storage import get_repository

logger = logging.getLogger(__name__)


def _cutoff(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=max(1, days))


def purge_expired_data(*, dry_run: bool = False, limit: int = 200) -> dict:
    """Elimina sesiones de chat y progreso de auditoría más antiguos que la retención."""
    repo = get_repository()
    chat_days = int(DATA_CONTROLLER.get("retention_chat_days") or 365 * 5)
    audit_days = int(DATA_CONTROLLER.get("retention_audit_days") or 365 * 3)
    chat_cut = _cutoff(chat_days)
    audit_cut = _cutoff(audit_days)

    stale_sessions = repo.list_stale_chat_sessions(older_than=chat_cut, limit=limit)
    stale_emails = repo.list_stale_audit_progress_emails(older_than=audit_cut, limit=limit)

    purged_sessions = 0
    purged_audit = 0
    errors: list[str] = []

    for session in stale_sessions:
        sid = session.session_id or ""
        if ":" not in sid:
            continue
        channel, user_id = sid.split(":", 1)
        if dry_run:
            purged_sessions += 1
            continue
        try:
            erase_web_subject(user_id, channel=channel or "web")
            purged_sessions += 1
        except Exception as exc:
            errors.append(f"{sid}:{exc}")
            logger.exception("Retention purge falló para %s", sid)

    for email in stale_emails:
        if dry_run:
            purged_audit += 1
            continue
        try:
            # Archivo previo (misma política que DELETE /api/audit/progress)
            existing = repo.get_audit_portal_progress(email)
            if existing:
                repo.append_audit_progress_history(email, existing.payload)
            if repo.delete_audit_portal_progress(email):
                purged_audit += 1
        except Exception as exc:
            errors.append(f"audit:{email}:{exc}")
            logger.exception("Retention purge audit falló para %s", email)

    summary = {
        "ok": not errors,
        "dry_run": dry_run,
        "chat_retention_days": chat_days,
        "audit_retention_days": audit_days,
        "stale_sessions_found": len(stale_sessions),
        "stale_audit_found": len(stale_emails),
        "purged_sessions": purged_sessions,
        "purged_audit_progress": purged_audit,
        "errors": errors[:20],
    }
    logger.info("Retention purge summary: %s", summary)
    return summary
