"""Cumplimiento: ARCO web + retención."""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.storage import get_repository
from src.storage.models import ChatSession, Draft


def _arco_auth_env(monkeypatch) -> None:
    from src.config import get_settings
    from src.storage import reset_repository

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "arco-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "arco-session-secret-key-32chars!!")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("WEB_AUTH_ENABLED", "true")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    monkeypatch.delenv("RENDER", raising=False)
    get_settings.cache_clear()
    reset_repository()


async def _login_cookie(client: AsyncClient) -> tuple[str, str]:
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
    assert cookie
    status = await client.get("/auth/status", cookies={"agente_session": cookie})
    subject = status.json().get("subject_id")
    assert subject
    return cookie, subject


@pytest.mark.asyncio
async def test_arco_erase_clears_session_data(monkeypatch):
    from src.config import get_settings

    _arco_auth_env(monkeypatch)
    repo = get_repository()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        cookie, subject = await _login_cookie(client)
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


@pytest.mark.asyncio
async def test_arco_erase_requires_authenticated_session(monkeypatch):
    """Sin cookie → 401; no se puede borrar con solo ?user_id=."""
    from src.config import get_settings

    _arco_auth_env(monkeypatch)
    repo = get_repository()
    victim = "victim-bola-user"
    victim_sid = f"web:{victim}"
    repo.save_chat_session(
        ChatSession(
            session_id=victim_sid,
            channel="web",
            user_id=victim,
            messages=[{"role": "user", "content": "secreto víctima"}],
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unauth = await client.post(
            "/api/compliance/arco-erase",
            params={"user_id": victim},
        )
        assert unauth.status_code == 401
        assert repo.get_chat_session(victim_sid) is not None

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_arco_erase_ignores_query_user_id_bola(monkeypatch):
    """Cookie válida + ?user_id=ajeno → solo borra al titular de la sesión."""
    from src.config import get_settings

    _arco_auth_env(monkeypatch)
    repo = get_repository()
    victim = "otro-titular-arco"
    victim_sid = f"web:{victim}"
    repo.save_chat_session(
        ChatSession(
            session_id=victim_sid,
            channel="web",
            user_id=victim,
            messages=[{"role": "user", "content": "datos ajenos"}],
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        cookie, subject = await _login_cookie(client)
        own_sid = f"web:{subject}"
        repo.save_chat_session(
            ChatSession(
                session_id=own_sid,
                channel="web",
                user_id=subject,
                messages=[{"role": "user", "content": "mis datos"}],
            )
        )
        erased = await client.post(
            "/api/compliance/arco-erase",
            params={"user_id": victim},
            cookies={"agente_session": cookie},
        )
        assert erased.status_code == 200
        assert erased.json()["session_id"] == own_sid

    assert repo.get_chat_session(own_sid) is None
    assert repo.get_chat_session(victim_sid) is not None
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_arco_erase_rejects_when_auth_disabled(monkeypatch):
    """Con auth off, ARCO no acepta ?user_id= arbitrario (503)."""
    from src.config import get_settings
    from src.storage import reset_repository

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.delenv("RENDER", raising=False)
    get_settings.cache_clear()
    reset_repository()
    repo = get_repository()
    victim = "auth-off-victim"
    victim_sid = f"web:{victim}"
    repo.save_chat_session(
        ChatSession(
            session_id=victim_sid,
            channel="web",
            user_id=victim,
            messages=[{"role": "user", "content": "x"}],
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/compliance/arco-erase",
            params={"user_id": victim},
        )
        assert res.status_code == 503
        assert repo.get_chat_session(victim_sid) is not None

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_compliance_policy_arco_email(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("DATABASE_URL", "")
    get_settings.cache_clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/compliance/policy")
        assert res.status_code == 200
        data = res.json()
        assert data["arco_email"] == "privacidad@dbxsolutions.com"
        assert data["controller"]["contact_email"] == "privacidad@dbxsolutions.com"
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
