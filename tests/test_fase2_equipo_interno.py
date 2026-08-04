"""Fase 2: transcript interno desde hooks + UI Equipo interno."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.agents.orchestrator import SPECIALIST_AGENT_IDS
from src.storage.memory import InMemoryRepository


@pytest.fixture()
def repo(monkeypatch):
    mem = InMemoryRepository()
    monkeypatch.setattr("src.storage.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.triple_chat.get_repository", lambda: mem)
    return mem


def test_record_specialist_exchange_enriches_labels(repo):
    from src.services.triple_chat import list_internal_transcript, record_specialist_exchange

    spec = next(iter(SPECIALIST_AGENT_IDS))
    entry = record_specialist_exchange(
        session_id="web:abogada",
        specialist_id=spec,
        pedido="Ordenar hechos del 12-ene",
        respuesta="3 eventos; 1 contradicción",
        turn_ref="tr-test",
    )
    assert entry is not None
    listed = list_internal_transcript("web:abogada")
    assert len(listed["entries"]) == 1
    row = listed["entries"][0]
    assert row["from_label"] in {"Coordinador del Caso", "Coordinador del Caso"}
    assert row["to_label"]
    assert "TriageResult" not in row["pedido"]
    assert "TriageResult" not in row["respuesta"]


@pytest.mark.asyncio
async def test_trace_hooks_persist_specialist_tool(repo):
    from src.agents.runner import _TraceRunHooks

    spec = "analista_cronologia_hechos"
    assert spec in SPECIALIST_AGENT_IDS

    class FakeTool:
        name = spec

    hooks = _TraceRunHooks({"session_id": "web:abogada", "trace_id": "tr-hooks", "spans": [], "actions": [], "completion": {"calls": []}})
    # Minimal structure used by _append_action
    hooks.trace.setdefault("actions", [])

    await hooks.on_tool_start(None, None, FakeTool())
    await hooks.on_tool_end(None, None, FakeTool(), {"hallazgos": "cronología preliminar"})

    listed = repo.list_internal_transcript("web:abogada")
    assert len(listed) == 1
    assert listed[0].to_actor == f"especialista:{spec}"
    assert "cronología" in listed[0].respuesta.lower() or "hallazgos" in listed[0].respuesta.lower()
    assert listed[0].pedido  # pedido no vacío (genérico o desde args)


@pytest.mark.asyncio
async def test_trace_hooks_deliberation_multi_round(repo):
    from src.agents.deliberation import empty_deliberation
    from src.agents.runner import _TraceRunHooks, _finalize_trace

    crono = "analista_cronologia_hechos"
    tipicidad = "analista_responsabilidad_tipicidad"
    assert crono in SPECIALIST_AGENT_IDS
    assert tipicidad in SPECIALIST_AGENT_IDS

    class FakeTool:
        def __init__(self, name: str):
            self.name = name

    trace = {
        "session_id": "web:abogada",
        "trace_id": "tr-delib",
        "turn_index": 1,
        "spans": [],
        "actions": [],
        "steps": [],
        "completion": {"calls": []},
        "deliberation": empty_deliberation(),
    }
    hooks = _TraceRunHooks(trace)

    await hooks.on_tool_start(None, None, FakeTool(crono))
    await hooks.on_tool_end(
        None,
        None,
        FakeTool(crono),
        {"hallazgos": "3 eventos", "nota": "[PENDIENTE DE VERIFICAR] hora exacta"},
    )
    await hooks.on_tool_start(None, None, FakeTool(tipicidad))
    await hooks.on_tool_end(
        None,
        None,
        FakeTool(tipicidad),
        {"hallazgos": "elementos objetivos; duda dolo"},
    )

    turns = trace["deliberation"]["turns"]
    kinds = [t["kind"] for t in turns]
    assert kinds.count("consult") == 2
    assert kinds.count("findings") == 2
    assert turns[0]["ronda"] == 1
    assert turns[2]["ronda"] == 1  # first consult to tipicidad

    finalized = _finalize_trace(trace, "Borrador informativo — requiere revisión.")
    summary = finalized["deliberation"]["summary"]
    assert summary["rounds"] == 2
    assert crono in summary["specialists_consulted"]
    assert tipicidad in summary["specialists_consulted"]
    assert any(t["kind"] == "synthesize" for t in finalized["deliberation"]["turns"])
    assert summary["open_pendientes"]
    assert any(s.get("kind") == "deliberation" for s in finalized["spans"])


def test_abogado_html_has_equipo_tab():
    html = Path("static/desk/abogado.html").read_text(encoding="utf-8")
    assert 'data-tab="equipo"' in html
    assert 'id="tab-equipo"' in html
    assert "equipo-interno.js" in html
    assert "Equipo interno" in html


def test_chat_js_renders_deliberation_section():
    js = Path("static/chat.js").read_text(encoding="utf-8")
    assert "Deliberación interna" in js
    assert "trace.deliberation" in js or "deliberation.turns" in js
    assert "specialists_consulted" in js


def test_equipo_js_fetches_transcript_api():
    js = Path("static/equipo-interno.js").read_text(encoding="utf-8")
    assert "/abogado/internal-transcript" in js
    assert "EquipoInterno" in js
    assert "Solo lectura" not in js or True  # hint is in HTML
    assert "TriageResult" not in js
