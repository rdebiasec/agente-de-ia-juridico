"""Tests batch Udemy: ModelSettings, RunContext, pricing, smoke productización."""

from __future__ import annotations

import pytest

from src.agents.agent_cache import clear_agent_cache
from src.agents.orchestrator import (
    POC_AGENT_ID,
    SPECIALIST_AGENT_IDS,
    _model_for_agent,
    _model_settings_for_agent,
    build_analista_responsabilidad_tipicidad_agent,
    build_coordinador_caso_agent,
    build_orchestrator,
    build_redactor_documentos_juridicos_agent,
)
from src.agents.pricing import enrich_completion_with_cost, estimate_call_cost_usd
from src.agents.session_context import (
    FirmRunContext,
    bind_run_context,
    resolve_expediente_id,
)
from src.agents.skill_catalog import HIGH_RISK_AGENTS
from src.config import Settings, get_settings


@pytest.fixture
def option_a_settings(monkeypatch):
    clear_agent_cache()
    get_settings.cache_clear()
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    monkeypatch.setenv("OPENAI_MODEL_HIGH_RISK", "gpt-4.1")
    monkeypatch.setenv("AGENT_TEMPERATURE", "0.2")
    monkeypatch.setenv("AGENT_TEMPERATURE_HIGH_RISK", "0.1")
    get_settings.cache_clear()
    yield get_settings()
    clear_agent_cache()
    get_settings.cache_clear()


def test_option_a_model_defaults(option_a_settings):
    assert option_a_settings.openai_model == "gpt-4.1-mini"
    assert option_a_settings.openai_model_high_risk == "gpt-4.1"
    assert option_a_settings.agent_temperature == 0.2
    assert option_a_settings.agent_temperature_high_risk == 0.1
    assert Settings.model_fields["openai_model"].default == "gpt-4.1-mini"
    assert Settings.model_fields["openai_model_high_risk"].default == "gpt-4.1"


def test_model_settings_temperature_all_agents(option_a_settings):
    del option_a_settings
    poc = build_coordinador_caso_agent()
    tipicidad = build_analista_responsabilidad_tipicidad_agent()
    redactor = build_redactor_documentos_juridicos_agent()

    assert poc.model == "gpt-4.1-mini"
    assert tipicidad.model == "gpt-4.1-mini"
    assert redactor.model == "gpt-4.1"
    assert poc.model_settings.temperature == 0.2
    assert tipicidad.model_settings.temperature == 0.2
    assert redactor.model_settings.temperature == 0.1
    assert _model_for_agent(POC_AGENT_ID) == "gpt-4.1-mini"
    for agent_id in HIGH_RISK_AGENTS:
        assert _model_settings_for_agent(agent_id).temperature == 0.1


def test_firm_run_context_anti_idor():
    assert resolve_expediente_id("web:other") is None
    ctx = FirmRunContext(
        session_id="web:mine",
        expediente_id="web:mine",
        channel="web",
        user_id="abogada",
        involucra_menor=True,
        datos_sensibles=True,
    )
    with bind_run_context(ctx):
        assert resolve_expediente_id("web:mine") == "web:mine"
        assert resolve_expediente_id("web:other") is None
        assert resolve_expediente_id("") == "web:mine"
    assert resolve_expediente_id("web:mine") is None


def test_pricing_estimate_and_enrich():
    cost = estimate_call_cost_usd(
        model="gpt-4.1-mini",
        input_tokens=1000,
        output_tokens=500,
    )
    assert cost is not None
    assert abs(cost - (1000 * 0.40 + 500 * 1.60) / 1_000_000) < 1e-9

    calls = [
        {
            "model": "gpt-4.1-mini",
            "usage": {"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
        },
        {
            "model": "gpt-4.1",
            "usage": {"input_tokens": 2000, "output_tokens": 800, "total_tokens": 2800},
        },
    ]
    meta = enrich_completion_with_cost(calls)
    assert meta["priced_calls"] == 2
    assert meta["estimated_cost_usd"] is not None
    assert calls[0]["estimated_cost_usd"] is not None


def test_smoke_productizacion_surface(option_a_settings):
    """B05: superficie chat tipicidad + high-risk solo por plan + temp/model cableados."""
    del option_a_settings
    orch = build_orchestrator(
        require_tool_approval=False,
        include_high_risk_tools=False,
        focus_agent_id="analista_responsabilidad_tipicidad",
        use_cache=False,
    )
    tool_names = {getattr(t, "name", "") for t in (orch.tools or [])}
    assert "analista_responsabilidad_tipicidad" in tool_names
    assert "redactor_documentos_juridicos" not in tool_names
    assert "evaluador_derechos_fundamentales_tutela" not in tool_names
    assert orch.model_settings.temperature == 0.2
    assert "analista_responsabilidad_tipicidad" in SPECIALIST_AGENT_IDS


def test_sentry_scrub_masks_email():
    from src.observability.sentry_scrub import sentry_before_send

    event = {
        "message": "Fallo para abogada@despacho.com en radicado 12345678901234567",
        "extra": {"content": "víctima contactar 3001234567"},
        "request": {
            "data": {"message": "caso sensible"},
            "headers": {"Authorization": "Bearer x"},
        },
    }
    out = sentry_before_send(event, None)
    assert out is not None
    assert "abogada@despacho.com" not in out["message"]
    assert "[email]" in out["message"]
    assert out["request"]["headers"]["Authorization"] == "[redacted]"
