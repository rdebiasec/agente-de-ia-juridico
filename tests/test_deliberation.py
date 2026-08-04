"""Deliberación mediada Gerente↔especialistas (opción A)."""

from __future__ import annotations

from src.agents.deliberation import (
    append_deliberation_turn,
    empty_deliberation,
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
    )
    append_deliberation_turn(
        trace,
        kind="findings",
        specialist_id="analista_cronologia_hechos",
        pedido="Ordenar hechos",
        respuesta="Evento A; [PENDIENTE DE VERIFICAR] hora",
        ronda=1,
    )
    assert next_ronda_for(trace, "analista_cronologia_hechos") == 2

    summary = finalize_deliberation_summary(trace)
    assert summary["rounds"] == 1
    assert summary["specialists_consulted"] == ["analista_cronologia_hechos"]
    assert summary["open_pendientes"]
    assert any(t["kind"] == "synthesize" for t in trace["deliberation"]["turns"])

    out = _finalize_trace(trace, "Texto sin disclaimer")
    assert any(s.get("name") == "Deliberación: cierre de junta" for s in out["spans"])
