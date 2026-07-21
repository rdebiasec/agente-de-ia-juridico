"""Generación de planes de ejecución (Fase 1 — sin streaming)."""

from __future__ import annotations

import time
import uuid

from src.agents.execution_schemas import ExecutionPlan, PlanStep
from src.agents.guardrails import check_input
from src.agents.plan_patterns import build_steps_from_pattern, remember_from_plan
from src.agents.plan_templates import build_templated_steps, classify_plan_template, template_label
from src.agents.runner import _infer_destination_agent, _summarize_input
from src.agents.skill_catalog import (
    HITL_OUTPUT_AGENTS,
    HIGH_RISK_AGENTS,
    desk_label,
    primary_skill_for_agent,
    skill_io_lists,
    valid_skill_ids,
)
from src.storage import get_repository
from src.storage.models import ExecutionPlanRecord


def _new_plan_id() -> str:
    return f"pl-{uuid.uuid4().hex[:12]}"


def _risk_for_agent(agent_id: str) -> str:
    if agent_id in HIGH_RISK_AGENTS:
        return "alto"
    if agent_id == "analista_calidad_juridica":
        return "medio"
    return "bajo"


def _build_plan_steps(destination_agent: str, user_message: str) -> list[PlanStep]:
    steps: list[PlanStep] = []
    order = 1

    coord_skill = primary_skill_for_agent("coordinador_expediente_penal")
    cin, cout = skill_io_lists(coord_skill)
    steps.append(
        PlanStep(
            step_id=f"s{order:02d}",
            order=order,
            agent_id="coordinador_expediente_penal",
            skill_id=coord_skill,
            title="Clasificar consulta y etapa aparente",
            user_summary=(
                "Como coordinador del expediente, revisaré su consulta, identificaré la tarea "
                "y la etapa procesal aparente, y pediré apoyo al equipo interno cuando haga falta."
            ),
            inputs_expected=cin or ["solicitud del despacho", "resumen de caso", "documentos disponibles"],
            outputs_promised=cout or ["clasificación", "etapa aparente", "agentes requeridos"],
            estimated_risk="bajo",
            requires_hitl_output=False,
        )
    )
    order += 1

    if destination_agent != "coordinador_expediente_penal":
        spec_skill = primary_skill_for_agent(destination_agent)
        if spec_skill and spec_skill not in valid_skill_ids():
            spec_skill = None
        sin, sout = skill_io_lists(spec_skill)
        steps.append(
            PlanStep(
                step_id=f"s{order:02d}",
                order=order,
                agent_id=destination_agent,
                skill_id=spec_skill,
                title=f"Consulta al equipo interno — {desk_label(destination_agent)}",
                user_summary=(
                    f"Voy a pedir al equipo interno ({desk_label(destination_agent)}) que procese "
                    f"su solicitud con base en la clasificación previa y el expediente disponible."
                ),
                inputs_expected=sin or ["consulta clasificada", "hechos y documentos del caso"],
                outputs_promised=sout or ["análisis preliminar", "recomendaciones operativas"],
                depends_on=[steps[0].step_id],
                estimated_risk=_risk_for_agent(destination_agent),  # type: ignore[arg-type]
                requires_hitl_output=destination_agent in HITL_OUTPUT_AGENTS,
            )
        )
        order += 1

        if destination_agent in HITL_OUTPUT_AGENTS or _risk_for_agent(destination_agent) == "alto":
            cal_skill = primary_skill_for_agent("analista_calidad_juridica")
            cin2, cout2 = skill_io_lists(cal_skill)
            steps.append(
                PlanStep(
                    step_id=f"s{order:02d}",
                    order=order,
                    agent_id="analista_calidad_juridica",
                    skill_id=cal_skill,
                    title="Control de calidad jurídica",
                    user_summary=(
                        "Como coordinador, pediré al equipo de calidad revisar coherencia "
                        "estratégica, soporte fáctico y riesgos antes de entregarte la salida."
                    ),
                    inputs_expected=cin2 or ["borrador del especialista", "fuentes citadas"],
                    outputs_promised=cout2 or ["dictamen de conformidad", "hallazgos y ajustes"],
                    depends_on=[steps[-1].step_id],
                    estimated_risk="medio",
                    requires_hitl_output=False,
                )
            )

    return steps


def create_execution_plan(
    *,
    message: str,
    channel: str,
    session_id: str,
    user_id: str,
) -> tuple[ExecutionPlan | None, str | None]:
    """Genera y persiste un plan en estado pending_approval."""
    ok, err = check_input(message)
    if not ok:
        return None, err

    destination = _infer_destination_agent(message)
    pattern_reused = False
    template_kind = classify_plan_template(message)
    steps: list[PlanStep] | None = None

    pattern_hit = build_steps_from_pattern(session_id)
    if pattern_hit:
        steps, remembered_kind = pattern_hit
        pattern_reused = True
        if remembered_kind:
            template_kind = remembered_kind  # type: ignore[assignment]

    if steps is None:
        steps = build_templated_steps(template_kind, message, destination_agent=destination)
    if steps is None:
        steps = _build_plan_steps(destination, message)

    agents = list(dict.fromkeys(s.agent_id for s in steps))
    objective = _summarize_input(message)
    if len(objective) < 20:
        objective = f"Atender consulta penal-víctimas: {objective}"
    if template_kind != "generico":
        objective = f"[{template_label(template_kind)}] {objective}"

    plan = ExecutionPlan(
        plan_id=_new_plan_id(),
        session_id=session_id,
        initiator_user_id=user_id,
        channel=channel,
        user_message=message,
        objective=objective,
        agents_involved=agents,
        steps=steps,
        status="pending_approval",
        created_at_ms=int(time.time() * 1000),
        template_kind=template_kind,
        pattern_reused=pattern_reused,
    )

    record = ExecutionPlanRecord(
        plan_id=plan.plan_id,
        session_id=session_id,
        initiator_user_id=user_id,
        channel=channel,
        user_message=message,
        status=plan.status,
        payload=plan.to_dict(),
    )
    get_repository().save_execution_plan(record)
    return plan, None


def get_plan(plan_id: str) -> ExecutionPlan | None:
    record = get_repository().get_execution_plan(plan_id)
    if not record:
        return None
    return ExecutionPlan.model_validate(record.payload)


def approve_plan(
    plan_id: str,
    user_id: str,
    *,
    remember_pattern: bool = False,
) -> tuple[ExecutionPlan | None, str | None]:
    record = get_repository().get_execution_plan(plan_id)
    if not record:
        return None, "Plan no encontrado."
    plan = ExecutionPlan.model_validate(record.payload)
    if plan.initiator_user_id != user_id:
        return None, "Solo el iniciador puede aprobar este plan."
    if plan.status != "pending_approval":
        return None, f"El plan no está pendiente de aprobación (estado: {plan.status})."
    plan.status = "approved"
    plan.approved_at_ms = int(time.time() * 1000)
    plan.approved_by = user_id
    if remember_pattern:
        remember_from_plan(plan.session_id, plan)
    record.status = plan.status
    record.payload = plan.to_dict()
    get_repository().save_execution_plan(record)
    return plan, None


def reject_plan(plan_id: str, user_id: str, reason: str = "") -> tuple[ExecutionPlan | None, str | None]:
    record = get_repository().get_execution_plan(plan_id)
    if not record:
        return None, "Plan no encontrado."
    plan = ExecutionPlan.model_validate(record.payload)
    if plan.initiator_user_id != user_id:
        return None, "Solo el iniciador puede rechazar este plan."
    if plan.status != "pending_approval":
        return None, f"El plan no está pendiente de aprobación (estado: {plan.status})."
    plan.status = "rejected"
    plan.rejected_at_ms = int(time.time() * 1000)
    plan.rejection_reason = (reason or "").strip() or "Sin motivo indicado."
    record.status = plan.status
    record.payload = plan.to_dict()
    get_repository().save_execution_plan(record)
    return plan, None
