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
    assert trace.get("received_by_agent") in {"agente_coordinador_principal", "socio_coordinador", "orquestador"}
    assert trace.get("sent_to_agent") in {
        "agente_servicio_cliente",
        "agente_redaccion_documental",
        "atencion_cliente",
        "redaccion_escritos",
        "comunicacion_clientes",
        "redaccion_documental",
    }
    assert trace.get("skill_kan") in {"KAN-11", "KAN-13"}
    assert isinstance(trace.get("actions"), list)
    assert isinstance(trace.get("completion"), dict)
    assert "summary" in trace.get("completion", {})
    assert any(step.get("step") == "Revisión humana" and step.get("status") == "pending" for step in trace.get("steps", []))


@pytest.mark.asyncio
async def test_trace_followup_capability_is_active():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/chat",
            json={"message": "Haga seguimiento mensual de radicado y prepare informe de novedades.", "channel": "web", "user_id": "trace-followup"},
        )
    assert res.status_code == 200
    data = res.json()
    assert data["pending_review"] is True
    trace = data.get("trace") or {}
    assert trace.get("blocked") is False
    assert trace.get("human_review_required") is True
    assert trace.get("sent_to_agent") in {
        "agente_seguimiento_procesal",
        "seguimiento_procesal",
        "dependiente_judicial",
    }
    assert trace.get("skill_kan") == "KAN-14"
    assert isinstance(trace.get("completion"), dict)
    assert any(step.get("step") == "Enruté al especialista" and step.get("status") == "done" for step in trace.get("steps", []))


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
        assert all("received_by_agent" in trace for trace in payload["traces"])
        assert all("sent_to_agent" in trace for trace in payload["traces"])
        assert all("skill_kan" in trace for trace in payload["traces"])
        assert all("completion" in trace for trace in payload["traces"])

    get_settings.cache_clear()

