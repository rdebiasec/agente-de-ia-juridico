"""Validación de escenarios para Workflow Trace."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_trace_allowed_drafting_sets_pending_review():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/chat",
            json={"message": "Redacte un correo formal al cliente sobre próximos pasos.", "channel": "web", "user_id": "trace-allow"},
        )
    assert res.status_code == 200
    data = res.json()
    assert data["pending_review"] is True
    trace = data.get("trace") or {}
    assert trace.get("blocked") is False
    assert trace.get("human_review_required") is True
    assert any(step.get("step") == "Revisión humana" and step.get("status") == "pending" for step in trace.get("steps", []))


@pytest.mark.asyncio
async def test_trace_blocked_scope_has_no_pending_review():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/chat",
            json={"message": "Haga seguimiento mensual de radicado y alertas automáticas.", "channel": "web", "user_id": "trace-block"},
        )
    assert res.status_code == 200
    data = res.json()
    assert data["pending_review"] is False
    trace = data.get("trace") or {}
    assert trace.get("blocked") is True
    assert trace.get("human_review_required") is False
    assert any(step.get("step") == "Validé alcance de fase" and step.get("status") == "blocked" for step in trace.get("steps", []))


@pytest.mark.asyncio
async def test_debug_trace_returns_session_history(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "trace-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "trace-session-secret-key-32chars")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/auth/login",
            json={"username": "despacho", "password": "trace-secret-pass"},
        )
        assert login.status_code == 200
        cookie = login.cookies.get("agente_session")
        assert cookie

        for message in (
            "Prepare un mensaje breve al cliente.",
            "Explique riesgos preliminares del caso.",
        ):
            chat = await client.post(
                "/chat",
                json={"message": message, "channel": "web", "user_id": "trace-session"},
                cookies={"agente_session": cookie},
            )
            assert chat.status_code == 200

        trace_res = await client.get("/debug/trace/web:trace-session?limit=5", cookies={"agente_session": cookie})
        assert trace_res.status_code == 200
        payload = trace_res.json()
        assert payload["session_id"] == "web:trace-session"
        assert len(payload["traces"]) >= 2
        assert all("steps" in trace for trace in payload["traces"])

    get_settings.cache_clear()

