"""Tests Phase-2: guardrails SDK, plan vía POC, schemas, RAG fallback."""

from __future__ import annotations

import pytest
from pydantic import ValidationError


def test_borrador_documento_penal_schema():
    from src.agents.schemas import BorradorDocumentoPenal

    draft = BorradorDocumentoPenal(
        tipo="memorial",
        titulo="Impulso procesal",
        cuerpo="Solicito impulso del radicado…",
        pendientes_verificacion=["Confirmar radicado"],
    )
    assert draft.tipo == "memorial"
    with pytest.raises(ValidationError):
        BorradorDocumentoPenal(tipo="memorial", titulo=" ", cuerpo="x")


def test_orchestrator_has_sdk_guardrails_and_redactor_output_type():
    from src.agents.orchestrator import build_orchestrator, get_agent_by_id

    poc = build_orchestrator()
    assert poc.input_guardrails
    assert poc.output_guardrails
    redactor = get_agent_by_id("redactor_documentos_juridicos_penales")
    assert redactor is not None
    assert redactor.output_type is not None


@pytest.mark.asyncio
async def test_poc_input_guardrail_trips_on_hard_oos():
    from agents import GuardrailFunctionOutput

    from src.agents.sdk_guardrails import poc_input_guardrail

    result = await poc_input_guardrail.guardrail_function(None, None, "Quiero iniciar un divorcio contencioso")
    assert isinstance(result, GuardrailFunctionOutput)
    assert result.tripwire_triggered is True


@pytest.mark.asyncio
async def test_poc_input_guardrail_allows_penal_anchor():
    from src.agents.sdk_guardrails import poc_input_guardrail

    result = await poc_input_guardrail.guardrail_function(
        None, None, "Victima solicita tutela por vulneracion en proceso penal"
    )
    assert result.tripwire_triggered is False


def test_plan_step_session_is_isolated():
    from src.agents.plan_executor import _plan_step_session_id

    sid = _plan_step_session_id("web:abogado", "pl-abc", "s02")
    assert sid.startswith("web:abogado:plan:pl-abc:")
    assert "s02" in sid


@pytest.mark.asyncio
async def test_approve_and_execute_returns_poc_voice():
    from httpx import ASGITransport, AsyncClient

    from src.agents.orchestrator import POC_AGENT_ID
    from src.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/chat/plan",
            json={
                "message": "Redacte memorial de impulso procesal con radicado 12345.",
                "channel": "web",
                "user_id": "plan-poc-voice",
            },
        )
        plan_id = created.json()["plan_id"]
        exec_res = await client.post(
            f"/chat/plan/{plan_id}/approve-and-execute",
            json={"user_id": "plan-poc-voice"},
        )
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["agent"] == POC_AGENT_ID
    assert data.get("trace", {}).get("skill_reason", "").lower().find("poc") >= 0


def test_rag_fallback_flag_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from src.config import get_settings
    from src.services import rag

    get_settings.cache_clear()
    monkeypatch.setattr(rag.get_settings(), "openai_api_key", "")
    _ = rag.embed_texto("prueba fallback")
    assert rag.last_embed_used_local_fallback() is True
