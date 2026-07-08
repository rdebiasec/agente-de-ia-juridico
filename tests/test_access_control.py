"""SEC-01/02 — control de acceso por subject_id en cookie (BOLA)."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.auth.gate import COOKIE_NAME, create_session_token
from src.main import app


@pytest.fixture
def auth_env(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "test-secret-pass-long")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")
    monkeypatch.setenv("DEV_AUTO_LOGIN", "false")
    monkeypatch.delenv("RENDER", raising=False)
    yield
    get_settings.cache_clear()


def _cookie(subject_id: str) -> dict:
    token = create_session_token(
        "test-session-secret-key-32chars!!",
        username="despacho",
        subject_id=subject_id,
    )
    return {COOKIE_NAME: token}


@pytest.mark.asyncio
async def test_plan_bola_blocks_cross_subject(auth_env):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Cronología de hechos del caso.",
                "channel": "web",
                "user_id": "victim-user",
            },
            cookies=_cookie("owner-subject"),
        )
        assert created.status_code == 200
        plan_id = created.json()["plan_id"]

        own = await client.get(
            f"/chat/plan/{plan_id}",
            params={"user_id": "owner-subject"},
            cookies=_cookie("owner-subject"),
        )
        assert own.status_code == 200

        spoof = await client.get(
            f"/chat/plan/{plan_id}",
            params={"user_id": "owner-subject"},
            cookies=_cookie("attacker-subject"),
        )
        assert spoof.status_code == 403


@pytest.mark.asyncio
async def test_trace_bola_blocks_other_session(auth_env):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        allowed = await client.get(
            "/debug/trace/web:owner-subject",
            cookies=_cookie("owner-subject"),
        )
        assert allowed.status_code == 200

        denied = await client.get(
            "/debug/trace/web:owner-subject",
            cookies=_cookie("other-subject"),
        )
        assert denied.status_code == 403
