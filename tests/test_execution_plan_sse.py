"""Fase 2 — SSE y ejecución async de planes."""

import asyncio
import json

import pytest
from httpx import ASGITransport, AsyncClient

from src.agents.plan_events import PlanEventBroker
from src.agents.plan_executor import schedule_execute_async, wait_for_plan_completion
from src.agents.planner import approve_plan
from src.main import app


@pytest.fixture(autouse=True)
def reset_broker():
    PlanEventBroker.reset_singleton_for_tests()
    yield
    PlanEventBroker.reset_singleton_for_tests()


@pytest.mark.asyncio
async def test_execute_returns_202():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Cronología de hechos del caso penal.",
                "channel": "web",
                "user_id": "sse-user-1",
            },
        )
        plan_id = created.json()["plan_id"]
        await client.post(
            f"/chat/plan/{plan_id}/approve",
            json={"user_id": "sse-user-1"},
        )
        exec_res = await client.post(
            f"/chat/plan/{plan_id}/execute",
            json={"user_id": "sse-user-1"},
        )
    assert exec_res.status_code == 202
    assert exec_res.json().get("status") == "executing"


@pytest.mark.asyncio
async def test_broker_emits_terminal_events():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Evalúe ruta procesal Ley 906.",
                "channel": "web",
                "user_id": "sse-user-2",
            },
        )
        plan_id = created.json()["plan_id"]
        approve_plan(plan_id, "sse-user-2")
        await schedule_execute_async(plan_id, "sse-user-2")
        await wait_for_plan_completion(plan_id, "sse-user-2", timeout=30.0)

    broker = PlanEventBroker.get()
    events = broker.get_history(plan_id)
    names = {e.get("event") for e in events}
    assert "execution_started" in names
    assert "step_started" in names
    assert "step_done" in names
    assert "plan_done" in names


@pytest.mark.asyncio
async def test_sse_replays_events_after_execution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Evalúe ruta procesal Ley 906.",
                "channel": "web",
                "user_id": "sse-user-2b",
            },
        )
        plan_id = created.json()["plan_id"]
        await client.post(f"/chat/plan/{plan_id}/approve", json={"user_id": "sse-user-2b"})
        await client.post(f"/chat/plan/{plan_id}/execute", json={"user_id": "sse-user-2b"})

        for _ in range(30):
            await asyncio.sleep(0.1)
            probe = await client.get(
                f"/chat/plan/{plan_id}/result",
                params={"user_id": "sse-user-2b"},
            )
            if probe.status_code == 200:
                break

        events: list[dict] = []
        async with client.stream(
            "GET",
            f"/chat/plan/{plan_id}/events",
            params={"user_id": "sse-user-2b"},
            timeout=10.0,
        ) as stream:
            async for line in stream.aiter_lines():
                if line.startswith("data: "):
                    events.append(json.loads(line[6:]))
                if events and events[-1].get("event") in ("plan_done", "plan_failed"):
                    break
                if len(events) > 40:
                    break

    names = {e.get("event") for e in events}
    assert "plan_done" in names


@pytest.mark.asyncio
async def test_plan_result_after_execution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Seguimiento de radicado penal.",
                "channel": "web",
                "user_id": "sse-user-3",
            },
        )
        plan_id = created.json()["plan_id"]
        await client.post(f"/chat/plan/{plan_id}/approve", json={"user_id": "sse-user-3"})
        await client.post(f"/chat/plan/{plan_id}/execute", json={"user_id": "sse-user-3"})

        result = None
        for _ in range(30):
            await asyncio.sleep(0.1)
            res = await client.get(
                f"/chat/plan/{plan_id}/result",
                params={"user_id": "sse-user-3"},
            )
            if res.status_code == 200 and res.json().get("result"):
                result = res.json()["result"]
                break

    assert result is not None
    assert result.get("text")
    assert result.get("trace", {}).get("trace_version") == "5.0"


@pytest.mark.asyncio
async def test_legacy_approve_and_execute_still_works():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Redacte solicitud de impulso procesal.",
                "channel": "web",
                "user_id": "sse-legacy",
            },
        )
        plan_id = created.json()["plan_id"]
        res = await client.post(
            f"/chat/plan/{plan_id}/approve-and-execute",
            json={"user_id": "sse-legacy"},
        )
    assert res.status_code == 200
    assert res.json().get("text")


@pytest.mark.asyncio
async def test_web_flow_no_regression():
    """Flujo web Fase 2: plan → approve → execute → result."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Cronología y vacíos probatorios del caso.",
                "channel": "web",
                "user_id": "flow-user",
            },
        )
        assert created.status_code == 200
        plan_id = created.json()["plan_id"]
        approved = await client.post(
            f"/chat/plan/{plan_id}/approve",
            json={"user_id": "flow-user"},
        )
        assert approved.status_code == 200
        exec_res = await client.post(
            f"/chat/plan/{plan_id}/execute",
            json={"user_id": "flow-user"},
        )
        assert exec_res.status_code == 202

        result = None
        for _ in range(30):
            await asyncio.sleep(0.1)
            res = await client.get(
                f"/chat/plan/{plan_id}/result",
                params={"user_id": "flow-user"},
            )
            if res.status_code == 200 and res.json().get("result"):
                result = res.json()["result"]
                break

    assert result is not None
    assert result.get("plan_id") == plan_id
    assert result.get("trace", {}).get("execution_plan_id") == plan_id


@pytest.mark.asyncio
async def test_execute_retry_after_failed():
    from src.storage import get_repository

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Evalúe ruta procesal.",
                "channel": "web",
                "user_id": "retry-user",
            },
        )
        plan_id = created.json()["plan_id"]
        await client.post(f"/chat/plan/{plan_id}/approve", json={"user_id": "retry-user"})
        record = get_repository().get_execution_plan(plan_id)
        assert record is not None
        record.status = "failed"
        payload = dict(record.payload or {})
        payload["status"] = "failed"
        record.payload = payload
        get_repository().save_execution_plan(record)

        retry = await client.post(
            f"/chat/plan/{plan_id}/execute",
            json={"user_id": "retry-user"},
        )
    assert retry.status_code == 202
    assert retry.json().get("status") == "executing"


@pytest.mark.asyncio
async def test_sse_requires_session(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "test-secret-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars")
    monkeypatch.setenv("DEV_AUTO_LOGIN", "false")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/chat/plan/pl-test/events", params={"user_id": "web"})
    assert res.status_code == 401

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_slack_plan_handler_execute_keyword():
    from src.channels.slack_plan import _pending_plans, handle_slack_plan_message

    _pending_plans.clear()
    messages: list[str] = []

    async def say(text, thread_ts=None):
        messages.append(text)

    handled = await handle_slack_plan_message(
        text="Necesito cronología de hechos",
        user_id="U123",
        say=say,
        thread_ts="T1",
    )
    assert handled is True
    assert _pending_plans.get("T1")

    handled2 = await handle_slack_plan_message(
        text="EJECUTAR",
        user_id="U123",
        say=say,
        thread_ts="T1",
    )
    assert handled2 is True
    assert any("Plan aprobado" in m or "Ejecución completada" in m or "↳" in m for m in messages)


@pytest.mark.asyncio
async def test_slack_plan_execute_survives_memory_cache_clear(monkeypatch):
    """Simula redeploy: caché RAM vacía pero plan pending sigue en el repositorio."""
    from src.channels import slack_plan
    from src.channels.slack_plan import _pending_plans, handle_slack_plan_message
    from src.config import get_settings
    from src.storage import get_repository, reset_repository

    monkeypatch.setenv("DATABASE_URL", "")
    get_settings.cache_clear()
    reset_repository()

    async def _fake_schedule(plan_id, user_id, on_step_message=None):
        return {"ok": True}

    async def _fake_wait(plan_id, user_id, timeout=90.0):
        return {"text": "Ejecución completada (test).", "session_id": f"slack:{user_id}", "trace": {}}

    monkeypatch.setattr(slack_plan, "schedule_execute_async", _fake_schedule)
    monkeypatch.setattr(slack_plan, "wait_for_plan_completion", _fake_wait)

    _pending_plans.clear()
    messages: list[str] = []

    async def say(text, thread_ts=None):
        messages.append(text)

    await handle_slack_plan_message(
        text="Necesito matriz hecho-prueba del caso",
        user_id="U999",
        say=say,
        thread_ts="T-RESTART",
    )
    plan_id = _pending_plans.get("T-RESTART")
    assert plan_id
    record = get_repository().get_execution_plan(plan_id)
    assert record is not None
    assert record.status == "pending_approval"
    assert (record.payload or {}).get("slack_thread_key") == "T-RESTART"

    # Reinicio de proceso: solo se pierde la caché en memoria
    _pending_plans.clear()

    await handle_slack_plan_message(
        text="EJECUTAR",
        user_id="U999",
        say=say,
        thread_ts="T-RESTART",
    )
    joined = "\n".join(messages)
    assert "No hay un plan pendiente" not in joined
    assert "Plan aprobado" in joined
    assert "Ejecución completada" in joined
    get_settings.cache_clear()
    reset_repository()
