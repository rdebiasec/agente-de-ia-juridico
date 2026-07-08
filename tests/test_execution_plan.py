"""Fase 1 — planes de ejecución con aprobación obligatoria."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_create_plan_returns_pending_approval():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/chat/plan",
            json={
                "message": "Necesito cronología de hechos del caso y vacíos probatorios.",
                "channel": "web",
                "user_id": "plan-user-1",
            },
        )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pending_approval"
    assert data["plan_id"].startswith("pl-")
    plan = data["plan"]
    assert plan["objective"]
    assert len(plan["steps"]) >= 1
    assert plan["steps"][0]["agent_id"] == "coordinador_expediente_penal"
    assert any(
        s["agent_id"] == "analista_cronologia_hechos_penales" for s in plan["steps"]
    )


@pytest.mark.asyncio
async def test_cannot_execute_without_approval():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Evalúe ruta procesal Ley 906 para la víctima.",
                "channel": "web",
                "user_id": "plan-user-2",
            },
        )
        plan_id = created.json()["plan_id"]
        from src.agents.plan_executor import execute_approved_plan

        result = await execute_approved_plan(plan_id, "plan-user-2")
    assert result.get("status_code") == 409


@pytest.mark.asyncio
async def test_approve_and_execute_trace_v5():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Redacte memorial de impulso procesal con radicado 12345.",
                "channel": "web",
                "user_id": "plan-user-3",
            },
        )
        plan_id = created.json()["plan_id"]
        exec_res = await client.post(
            f"/chat/plan/{plan_id}/approve-and-execute",
            json={"user_id": "plan-user-3"},
        )
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["text"]
    trace = data.get("trace") or {}
    assert trace.get("trace_version") == "5.0"
    assert trace.get("execution_plan_id") == plan_id
    assert isinstance(trace.get("agent_io_reports"), list)
    assert len(trace["agent_io_reports"]) >= 1
    assert isinstance(trace.get("user_updates"), list)
    assert data.get("pending_review") is True


@pytest.mark.asyncio
async def test_reject_plan():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Seguimiento de radicado y alertas de vencimiento.",
                "channel": "web",
                "user_id": "plan-user-4",
            },
        )
        plan_id = created.json()["plan_id"]
        rejected = await client.post(
            f"/chat/plan/{plan_id}/reject",
            json={"user_id": "plan-user-4", "reason": "Falta incluir etapa procesal"},
        )
        fetched = await client.get(f"/chat/plan/{plan_id}", params={"user_id": "plan-user-4"})
    assert rejected.status_code == 200
    assert fetched.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_legacy_chat_still_works():
    """Slack y regresión: POST /chat directo sigue operativo."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/chat",
            json={
                "message": "Haga seguimiento mensual de radicado.",
                "channel": "web",
                "user_id": "plan-legacy",
            },
        )
    assert res.status_code == 200
    assert res.json().get("text")
