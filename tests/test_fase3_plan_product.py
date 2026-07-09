"""Fase 3 — plantillas, patrones, export MD y dashboard."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from src.agents.plan_export import markdown_from_record, render_plan_markdown
from src.agents.plan_patterns import build_steps_from_pattern, remember_from_plan, reset_all_patterns_for_tests
from src.agents.plan_templates import build_templated_steps, classify_plan_template
from src.agents.planner import approve_plan, create_execution_plan
from src.main import app
from src.storage import get_repository
from src.storage.models import ExecutionPlanRecord


async def _login_web(client: AsyncClient, monkeypatch: pytest.MonkeyPatch, password: str = "fase3-web-pass-long!!") -> None:
    from src.config import get_settings

    monkeypatch.setenv("SITE_PASSWORD", password)
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")
    get_settings.cache_clear()
    login = await client.post(
        "/auth/login",
        json={"username": "despacho", "password": password},
    )
    assert login.status_code == 200, login.text


@pytest.fixture(autouse=True)
def clean_patterns():
    reset_all_patterns_for_tests()
    yield
    reset_all_patterns_for_tests()


def test_classify_plan_template_cronologia():
    assert classify_plan_template("Necesito una cronología de hechos del caso") == "cronologia"


def test_classify_plan_template_tutela():
    assert classify_plan_template("Evaluar acción de tutela por derecho fundamental") == "tutela"


def test_templated_steps_cronologia_has_analyst():
    steps = build_templated_steps("cronologia", "cronología de hechos")
    assert steps is not None
    agents = [s.agent_id for s in steps]
    assert "analista_cronologia_hechos_penales" in agents


def test_remember_pattern_reused_on_second_plan():
    plan1, err = create_execution_plan(
        message="Cronología de hechos del expediente.",
        channel="web",
        session_id="web:pattern-user",
        user_id="pattern-user",
    )
    assert err is None and plan1
    approved, err2 = approve_plan(plan1.plan_id, "pattern-user", remember_pattern=True)
    assert err2 is None and approved

    plan2, err3 = create_execution_plan(
        message="Otra consulta sobre hechos del caso.",
        channel="web",
        session_id="web:pattern-user",
        user_id="pattern-user",
    )
    assert err3 is None and plan2
    assert plan2.pattern_reused is True
    assert len(plan2.steps) == len(plan1.steps)


def test_export_markdown_contains_plan_id():
    plan, _ = create_execution_plan(
        message="Audiencia de formulación de imputación.",
        channel="web",
        session_id="web:export-user",
        user_id="export-user",
    )
    assert plan
    record = get_repository().get_execution_plan(plan.plan_id)
    assert record
    md = markdown_from_record(record)
    assert plan.plan_id in md
    assert "Plan de ejecución" in md


def test_render_plan_markdown_template_label():
    plan, _ = create_execution_plan(
        message="Preparar audiencia de juicio oral.",
        channel="web",
        session_id="web:md-user",
        user_id="md-user",
    )
    assert plan and plan.template_kind == "audiencia"
    md = render_plan_markdown(plan)
    assert "audiencia" in md.lower()


@pytest.mark.asyncio
async def test_chat_plan_export_md_endpoint(monkeypatch):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await _login_web(client, monkeypatch)
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Cronología breve de hechos.",
                "channel": "web",
                "user_id": "export-api",
            },
        )
        assert created.status_code == 200, created.text
        plan_id = created.json()["plan_id"]
        res = await client.get(f"/chat/plan/{plan_id}/export.md?user_id=export-api")
    assert res.status_code == 200
    assert "text/markdown" in res.headers.get("content-type", "")
    assert plan_id in res.text


@pytest.mark.asyncio
async def test_audit_execution_dashboard_requires_auth(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "audit-dash-pass-long")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unauth = await client.get("/api/audit/execution-plans/dashboard")
        assert unauth.status_code == 401

        prelogin = await client.post(
            "/api/audit/prelogin",
            json={"email": "auditor@despacho.com", "password": "audit-dash-pass-long"},
        )
        assert prelogin.status_code == 200, prelogin.text
        login_body: dict = {
            "email": "auditor@despacho.com",
            "password": "audit-dash-pass-long",
            "accept_privacy": True,
            "accept_sensitive_data": True,
        }
        state = prelogin.json()
        if state.get("needs_pin_setup"):
            login_body["new_pin"] = "123456"
        else:
            login_body["pin"] = "123456"
        login = await client.post("/api/audit/login", json=login_body)
        if login.status_code == 200:
            dash = await client.get("/api/audit/execution-plans/dashboard")
            assert dash.status_code == 200
            body = dash.json()
            assert "total" in body
            assert "recent" in body

    get_settings.cache_clear()


def test_execution_plan_stats_in_repository():
    repo = get_repository()
    plan, _ = create_execution_plan(
        message="Cronología de hechos.",
        channel="web",
        session_id="web:stats-user",
        user_id="stats-user",
    )
    assert plan
    stats = repo.execution_plan_stats()
    assert stats["total"] >= 1
    assert "by_template" in stats
    assert "by_status" in stats
    assert any(r["plan_id"] == plan.plan_id for r in stats["recent"])
    row = next(r for r in stats["recent"] if r["plan_id"] == plan.plan_id)
    assert row.get("steps_count", 0) >= 1
    assert "user_message_preview" in row


@pytest.mark.asyncio
async def test_audit_clear_execution_plans(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "audit-clear-plans-pass")
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars!!")
    monkeypatch.setenv("DATABASE_URL", "")

    create_execution_plan(
        message="Plan para borrar.",
        channel="web",
        session_id="web:clear-user",
        user_id="clear-user",
    )
    repo = get_repository()
    assert repo.execution_plan_stats()["total"] >= 1

    email = "clear@despacho.com"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        unauth = await client.delete("/api/audit/execution-plans")
        assert unauth.status_code == 401

        login_body: dict = {
            "email": email,
            "password": "audit-clear-plans-pass",
            "accept_privacy": True,
            "accept_sensitive_data": True,
        }
        prelogin = await client.post(
            "/api/audit/prelogin",
            json={"email": email, "password": "audit-clear-plans-pass"},
        )
        assert prelogin.status_code == 200, prelogin.text
        state = prelogin.json()
        if state.get("needs_pin_setup"):
            login_body["new_pin"] = "112233"
        else:
            login_body["pin"] = "112233"

        login = await client.post("/api/audit/login", json=login_body)
        assert login.status_code == 200

        cleared = await client.delete("/api/audit/execution-plans")
        assert cleared.status_code == 200
        body = cleared.json()
        assert body["ok"] is True
        assert body["deleted"] >= 1

        dash = await client.get("/api/audit/execution-plans/dashboard")
        assert dash.json()["total"] == 0

    get_settings.cache_clear()
