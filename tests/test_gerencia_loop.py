"""Invariantes del loop del Coordinador del Caso."""

from __future__ import annotations

from src.agents.completeness import assess_completeness, persist_verification
from src.agents.planner import approve_plan, create_execution_plan
from src.storage import get_repository
from src.storage.models import Expediente


def test_incomplete_high_risk_plan_never_contains_specialist():
    plan, err = create_execution_plan(
        message="Redacte un memorial de impulso para la víctima.",
        channel="web",
        session_id="web:gate-incomplete",
        user_id="gate-incomplete",
    )
    assert err is None and plan is not None
    assert plan.status == "awaiting_input"
    assert plan.triage_snapshot["puede_continuar"] is False
    assert plan.triage_snapshot["datos_faltantes_bloqueantes"]
    assert [step.agent_id for step in plan.steps] == ["coordinador_caso"]

    approved, approval_error = approve_plan(plan.plan_id, "gate-incomplete")
    assert approved is None
    assert "no está pendiente de aprobación" in (approval_error or "")


def test_complete_high_risk_plan_can_reach_specialist():
    plan, err = create_execution_plan(
        message=(
            "Redacte memorial de impulso. Radicado 11001-60-00-2026-123456. "
            "La víctima denunció lesiones y aportó el relato. Tengo poder firmado. "
            "Última actuación: audiencia de imputación. Partes: víctima y procesado."
        ),
        channel="web",
        session_id="web:gate-complete",
        user_id="gate-complete",
    )
    assert err is None and plan is not None
    assert plan.status == "pending_approval"
    assert plan.triage_snapshot["puede_continuar"] is True
    assert any(
        step.agent_id == "redactor_documentos_juridicos" for step in plan.steps
    )


def test_ledger_closes_faltantes_when_new_data_arrives():
    session_id = "web:ledger-close"
    exp = Expediente(session_id=session_id)
    first = assess_completeness(
        "Redacte memorial de impulso.",
        destination="redactor_documentos_juridicos",
        expediente=exp,
    )
    persist_verification(
        exp,
        first,
        destination="redactor_documentos_juridicos",
    )
    stored = get_repository().get_expediente(session_id)
    assert stored is not None
    assert stored.faltantes_gerencia
    assert any(task["estado"] == "pendiente" for task in stored.tareas_gerencia)

    stored.radicado = "11001-60-00-2026-123456"
    second = assess_completeness(
        (
            "La víctima denunció lesiones y aportó el relato. Tengo poder firmado. "
            "Última actuación: audiencia de imputación. Partes: víctima y procesado."
        ),
        destination="redactor_documentos_juridicos",
        expediente=stored,
    )
    persist_verification(
        stored,
        second,
        destination="redactor_documentos_juridicos",
    )
    refreshed = get_repository().get_expediente(session_id)
    assert refreshed is not None
    assert refreshed.faltantes_gerencia == []
    assert all(task["estado"] == "cerrada" for task in refreshed.tareas_gerencia)
    assert refreshed.metricas_gerencia["verificaciones"] >= 2

