"""Deliberación mediada Gerente↔especialistas (opción A)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.agents.deliberation import (
    append_deliberation_turn,
    empty_deliberation,
    emit_openai_deliberation_span,
    finalize_deliberation_summary,
    next_ronda_for,
)
from src.agents.runner import _base_trace, _finalize_trace


def test_base_trace_has_deliberation_v41():
    trace = _base_trace("web:test", "web", "Ordene hechos del caso VIF")
    assert trace["trace_version"] == "4.1"
    assert trace["deliberation"]["protocol"] == "gerente_especialista_v1"
    assert trace["deliberation"]["turns"] == []


def test_finalize_adds_synthesize_and_summary():
    trace = {
        "turn_index": 2,
        "spans": [],
        "actions": [],
        "steps": [],
        "deliberation": empty_deliberation(),
    }
    append_deliberation_turn(
        trace,
        kind="consult",
        specialist_id="analista_cronologia_hechos",
        pedido="Ordenar hechos",
        reasoning="Necesito línea de tiempo",
        ronda=1,
        emit_openai=False,
    )
    append_deliberation_turn(
        trace,
        kind="findings",
        specialist_id="analista_cronologia_hechos",
        pedido="Ordenar hechos",
        respuesta="Evento A; [PENDIENTE DE VERIFICAR] hora",
        ronda=1,
        emit_openai=False,
    )
    assert next_ronda_for(trace, "analista_cronologia_hechos") == 2

    summary = finalize_deliberation_summary(trace)
    assert summary["rounds"] == 1
    assert summary["specialists_consulted"] == ["analista_cronologia_hechos"]
    assert summary["open_pendientes"]
    assert any(t["kind"] == "synthesize" for t in trace["deliberation"]["turns"])

    out = _finalize_trace(trace, "Texto sin disclaimer")
    assert any(s.get("name") == "Deliberación: cierre de junta" for s in out["spans"])


def test_emit_openai_span_noop_without_current_trace(monkeypatch):
    monkeypatch.setattr(
        "agents.tracing.get_current_trace",
        lambda: None,
    )
    ok = emit_openai_deliberation_span(
        "consult",
        specialist_id="analista_cronologia_hechos",
        pedido="Ordenar hechos",
        ronda=1,
    )
    assert ok is False


def test_emit_openai_span_uses_custom_span(monkeypatch):
    recorded: list[dict[str, Any]] = []

    @contextmanager
    def fake_custom_span(*, name: str, data: dict | None = None, **_kwargs):
        recorded.append({"name": name, "data": dict(data or {})})
        yield MagicMock()

    monkeypatch.setattr("agents.tracing.get_current_trace", lambda: object())
    monkeypatch.setattr("agents.tracing.custom_span", fake_custom_span)

    ok = emit_openai_deliberation_span(
        "findings",
        specialist_id="analista_responsabilidad_tipicidad",
        pedido="Analizar dolo",
        respuesta="Dolo eventual plausible; [PENDIENTE DE VERIFICAR] pericia",
        reasoning="Contraste con cronología",
        ronda=2,
        extra={"rounds": 2},
    )
    assert ok is True
    assert len(recorded) == 1
    assert recorded[0]["name"] == "deliberation.findings"
    data = recorded[0]["data"]
    assert data["protocol"] == "gerente_especialista_v1"
    assert data["kind"] == "findings"
    assert data["specialist_id"] == "analista_responsabilidad_tipicidad"
    assert data["ronda"] == 2
    assert "pedido" in data and "Analizar dolo" in data["pedido"]
    assert data["rounds"] == 2


@pytest.mark.asyncio
async def test_hooks_emit_openai_spans_on_consult_findings(monkeypatch):
    from src.agents.orchestrator import SPECIALIST_AGENT_IDS
    from src.agents.runner import _TraceRunHooks

    recorded: list[str] = []

    @contextmanager
    def fake_custom_span(*, name: str, data: dict | None = None, **_kwargs):
        recorded.append(name)
        yield MagicMock()

    monkeypatch.setattr("agents.tracing.get_current_trace", lambda: object())
    monkeypatch.setattr("agents.tracing.custom_span", fake_custom_span)

    spec = "analista_cronologia_hechos"
    assert spec in SPECIALIST_AGENT_IDS

    class FakeTool:
        name = spec

    hooks = _TraceRunHooks(
        {
            "session_id": "web:delib-openai",
            "trace_id": "tr-openai",
            "spans": [],
            "actions": [],
            "completion": {"calls": []},
            "deliberation": empty_deliberation(),
        }
    )
    await hooks.on_tool_start(None, None, FakeTool())
    await hooks.on_tool_end(None, None, FakeTool(), {"hallazgos": "ok"})

    class FakePoc:
        name = "coordinador_caso"

    await hooks.on_agent_end(None, FakePoc(), "síntesis")

    assert "deliberation.consult" in recorded
    assert "deliberation.findings" in recorded
    assert "deliberation.synthesize" in recorded
    kinds = [t["kind"] for t in hooks.trace["deliberation"]["turns"]]
    assert kinds.count("consult") == 1
    assert kinds.count("findings") == 1
    assert kinds.count("synthesize") == 1
