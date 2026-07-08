"""Plantillas de plan por tipo de consulta (Fase 3)."""

from __future__ import annotations

import re
from typing import Literal

from src.agents.execution_schemas import PlanStep
from src.agents.runner import _infer_destination_agent
from src.agents.skill_catalog import (
    HITL_OUTPUT_AGENTS,
    HIGH_RISK_AGENTS,
    agent_display_name,
    primary_skill_for_agent,
    skill_io_lists,
    valid_skill_ids,
)

PlanTemplateKind = Literal["cronologia", "tutela", "audiencia", "generico"]

_TEMPLATE_LABELS: dict[PlanTemplateKind, str] = {
    "cronologia": "Cronología y hechos",
    "tutela": "Acción de tutela",
    "audiencia": "Preparación de audiencia",
    "generico": "Consulta general",
}

_TUTELA_RE = re.compile(r"\b(tutela|derecho fundamental|subsidiariedad|inmediatez)\b", re.IGNORECASE)
_AUDIENCIA_RE = re.compile(r"\b(audiencia|interrogatorio|contrainterrogatorio|juicio|alegato)\b", re.IGNORECASE)
_CRONOLOGIA_RE = re.compile(r"\b(cronolog[ií]a|linea de tiempo|hechos|narrativa factual|relato)\b", re.IGNORECASE)


def classify_plan_template(message: str) -> PlanTemplateKind:
    text = message or ""
    if _TUTELA_RE.search(text):
        return "tutela"
    if _AUDIENCIA_RE.search(text):
        return "audiencia"
    if _CRONOLOGIA_RE.search(text):
        return "cronologia"
    return "generico"


def template_label(kind: PlanTemplateKind) -> str:
    return _TEMPLATE_LABELS.get(kind, _TEMPLATE_LABELS["generico"])


def _risk_for_agent(agent_id: str) -> str:
    if agent_id in HIGH_RISK_AGENTS:
        return "alto"
    if agent_id == "analista_calidad_juridica":
        return "medio"
    return "bajo"


def _step(
    *,
    step_id: str,
    order: int,
    agent_id: str,
    title: str,
    user_summary: str,
    depends_on: list[str] | None = None,
) -> PlanStep:
    skill = primary_skill_for_agent(agent_id)
    if skill and skill not in valid_skill_ids():
        skill = None
    sin, sout = skill_io_lists(skill)
    return PlanStep(
        step_id=step_id,
        order=order,
        agent_id=agent_id,
        skill_id=skill,
        title=title,
        user_summary=user_summary,
        inputs_expected=sin or ["consulta del despacho", "expediente disponible"],
        outputs_promised=sout or ["análisis preliminar", "recomendaciones"],
        depends_on=depends_on or [],
        estimated_risk=_risk_for_agent(agent_id),  # type: ignore[arg-type]
        requires_hitl_output=agent_id in HITL_OUTPUT_AGENTS,
    )


def build_templated_steps(
    kind: PlanTemplateKind,
    message: str,
    *,
    destination_agent: str | None = None,
) -> list[PlanStep] | None:
    """Genera pasos según plantilla; None si debe usarse el plan genérico Fase 1."""
    if kind == "generico":
        return None

    destination = destination_agent or _infer_destination_agent(message)
    steps: list[PlanStep] = []
    order = 1
    steps.append(
        _step(
            step_id=f"s{order:02d}",
            order=order,
            agent_id="coordinador_expediente_penal",
            title="Clasificar consulta y contexto del caso",
            user_summary=(
                "Identificaré la tarea solicitada, la etapa procesal aparente y el especialista "
                "necesario para esta plantilla."
            ),
        )
    )
    order += 1

    if kind == "cronologia":
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id="analista_cronologia_hechos_penales",
                title="Construir cronología y matriz hecho-fuente",
                user_summary=(
                    "Extraeré hechos relevantes, ordenaré la línea de tiempo y señalaré "
                    "vacíos o contradicciones que requieran verificación."
                ),
                depends_on=[steps[0].step_id],
            )
        )
        order += 1
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id="analista_calidad_juridica",
                title="Control de calidad — cronología",
                user_summary="Revisaré coherencia factual y separación hecho/inferencia antes de entregar.",
                depends_on=[steps[-1].step_id],
            )
        )
    elif kind == "tutela":
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id="evaluador_derechos_fundamentales_tutela",
                title="Evaluar procedencia y derecho fundamental",
                user_summary=(
                    "Analizaré subsidiariedad, inmediatez y el derecho fundamental presuntamente "
                    "vulnerado antes de proponer redacción."
                ),
                depends_on=[steps[0].step_id],
            )
        )
        order += 1
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id="redactor_documentos_juridicos_penales",
                title="Borrador preliminar de tutela",
                user_summary=(
                    "Si procede, prepararé borrador con hechos, fundamentos y pretensiones "
                    "para revisión del despacho."
                ),
                depends_on=[steps[-1].step_id],
            )
        )
        order += 1
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id="analista_calidad_juridica",
                title="Control de calidad — tutela",
                user_summary="Verificaré tono, soporte normativo y riesgos de improcedencia.",
                depends_on=[steps[-1].step_id],
            )
        )
    elif kind == "audiencia":
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id="preparador_estrategico_audiencias_penales",
                title="Objetivo y estrategia de audiencia",
                user_summary=(
                    "Definiré el objetivo procesal de la audiencia, solicitudes orales y "
                    "preguntas clave para testigos o partes."
                ),
                depends_on=[steps[0].step_id],
            )
        )
        order += 1
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id="analista_calidad_juridica",
                title="Checklist previo a audiencia",
                user_summary="Revisaré riesgos procesales y coherencia estratégica antes de la intervención.",
                depends_on=[steps[-1].step_id],
            )
        )

    if destination not in {s.agent_id for s in steps} and destination != "coordinador_expediente_penal":
        spec = _step(
            step_id=f"s{order:02d}",
            order=order,
            agent_id=destination,
            title=f"Especialista adicional — {agent_display_name(destination)}",
            user_summary=f"Incorporaré el análisis de {agent_display_name(destination)} según su consulta.",
            depends_on=[steps[-1].step_id],
        )
        steps.append(spec)

    return steps
