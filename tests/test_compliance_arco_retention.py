"""Cumplimiento: ARCO web + retención."""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.storage import get_repository
from src.storage.models import ChatSession, Draft


@pytest.mark.asyncio
async def test_arco_erase_clears_session_data(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "arco-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "arco-session-secret-key-32chars!!")
    monkeypatch.setenv("DATABASE_URL", "")

    from src.storage import reset_repository

    reset_repository()
    repo = get_repository()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/auth/login",
            json={
                "username": "despacho",
                "password": "arco-secret-pass",
                "accept_privacy": True,
                "accept_sensitive_data": True,
            },
        )
        assert login.status_code == 200
        cookie = login.cookies.get("agente_session")
        status = await client.get("/auth/status", cookies={"agente_session": cookie})
        subject = status.json().get("subject_id")
        assert subject
        session_id = f"web:{subject}"
        repo.save_chat_session(
            ChatSession(
                session_id=session_id,
                channel="web",
                user_id=subject,
                messages=[{"role": "user", "content": "hola"}],
            )
        )
        repo.add_draft(
            Draft(session_id=session_id, contenido="borrador sensible", tipo="memorial", titulo="t")
        )
        erased = await client.post(
            "/api/compliance/arco-erase",
            cookies={"agente_session": cookie},
        )
        assert erased.status_code == 200
        body = erased.json()
        assert body["ok"] is True
        assert body["session_id"] == session_id

    assert repo.get_chat_session(session_id) is None
    assert repo.list_drafts(session_id=session_id) == []
    get_settings.cache_clear()


def test_retention_purge_dry_run_counts_stale():
    from src.compliance.retention import purge_expired_data
    from src.storage import reset_repository

    reset_repository()
    repo = get_repository()
    old = datetime.now(timezone.utc) - timedelta(days=365 * 6)
    repo.save_chat_session(
        ChatSession(
            session_id="web:old-user",
            channel="web",
            user_id="old-user",
            messages=[{"role": "user", "content": "x"}],
            updated_at=old,
            created_at=old,
        )
    )
    summary = purge_expired_data(dry_run=True, limit=50)
    assert summary["stale_sessions_found"] >= 1
    assert summary["purged_sessions"] >= 1
