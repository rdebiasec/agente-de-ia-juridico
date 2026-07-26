"""Ola 3: gate duro de calidad en planes de alto riesgo."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.agents.execution_schemas import PlanStep
from src.agents.plan_executor import _quality_gate_blocks
from src.agents.schemas import DictamenCalidad
from src.agents.structured_render import render_structured_output


def _step_calidad() -> PlanStep:
    return PlanStep(
        step_id="s03",
        order=3,
        agent_id="analista_calidad_juridica",
        skill_id="revisar_coherencia_estrategica",
        title="Control de calidad jurídica",
        user_summary="Revisión de calidad",
        estimated_risk="medio",
    )


def test_quality_gate_blocks_rechazado():
    result = SimpleNamespace(
        final_output=DictamenCalidad(
            veredicto="rechazado",
            hallazgos=["Cita inventada"],
            resumen="No entregable",
        )
    )
    blocked, msg = _quality_gate_blocks(result, _step_calidad())
    assert blocked is True
    assert "rechazado" in msg
    assert "No se entrega" in msg


def test_quality_gate_blocks_escalar():
    result = SimpleNamespace(
        final_output=DictamenCalidad(
            veredicto="escalar",
            hallazgos=["Riesgo reputacional"],
            resumen="Escalar al titular",
        )
    )
    blocked, msg = _quality_gate_blocks(result, _step_calidad())
    assert blocked is True
    assert "escalar" in msg


@pytest.mark.parametrize("veredicto", ["aprobable", "con_cambios"])
def test_quality_gate_allows_non_blocking(veredicto: str):
    result = SimpleNamespace(
        final_output=DictamenCalidad(
            veredicto=veredicto,  # type: ignore[arg-type]
            hallazgos=[],
            resumen="ok",
        )
    )
    blocked, msg = _quality_gate_blocks(result, _step_calidad())
    assert blocked is False
    assert msg == ""


def test_quality_gate_ignores_other_agents():
    step = PlanStep(
        step_id="s02",
        order=2,
        agent_id="redactor_documentos_juridicos_penales",
        skill_id="redactar_memorial_penal",
        title="Redacción",
        user_summary="Redactar",
        estimated_risk="alto",
    )
    result = SimpleNamespace(
        final_output=DictamenCalidad(veredicto="rechazado", resumen="x")
    )
    blocked, _ = _quality_gate_blocks(result, step)
    assert blocked is False


def test_render_dictamen_and_cronologia():
    text = render_structured_output(
        DictamenCalidad(veredicto="con_cambios", hallazgos=["Ajustar tono"], resumen="Revisar")
    )
    assert "con_cambios" in text
    assert "Ajustar tono" in text


def test_schemas_bloquea_entrega_property():
    assert DictamenCalidad(veredicto="rechazado", resumen="x").bloquea_entrega is True
    assert DictamenCalidad(veredicto="aprobable", resumen="x").bloquea_entrega is False
