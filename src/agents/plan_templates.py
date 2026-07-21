"""Plantillas de plan por tipo de consulta (Fase 3 + flujos SPOA frecuentes)."""

from __future__ import annotations

import re
from typing import Literal

from src.agents.execution_schemas import PlanStep
from src.agents.runner import _infer_destination_agent
from src.agents.skill_catalog import (
    HITL_OUTPUT_AGENTS,
    HIGH_RISK_AGENTS,
    desk_label,
    primary_skill_for_agent,
    skill_io_lists,
    valid_skill_ids,
)

PlanTemplateKind = Literal[
    "cronologia",
    "tutela",
    "audiencia",
    "indagacion_impulso",
    "vif_proteccion",
    "querella_abreviado",
    "generico",
]

_TEMPLATE_LABELS: dict[PlanTemplateKind, str] = {
    "cronologia": "Cronología y hechos",
    "tutela": "Acción de tutela",
    "audiencia": "Preparación de audiencia",
    "indagacion_impulso": "Impulso / anti-archivo en indagación",
    "vif_proteccion": "VIF y medidas de protección",
    "querella_abreviado": "Querella / procedimiento abreviado",
    "generico": "Consulta general",
}

_TUTELA_RE = re.compile(r"\b(tutela|derecho fundamental|subsidiariedad|inmediatez)\b", re.IGNORECASE)
_VIF_RE = re.compile(
    r"\b(violencia\s+intrafamiliar|v\.?\s*i\.?\s*f\.?|inasistencia\s+alimentaria|"
    r"medidas?\s+de\s+protecci[oó]n|enfoque\s+diferencial|revictimizaci[oó]n)\b",
    re.IGNORECASE,
)
_QUERELLA_RE = re.compile(
    r"\b(querella|procedimiento\s+abreviado|ley\s+1826|audiencia\s+concentrada)\b",
    re.IGNORECASE,
)
_IMPULSO_RE = re.compile(
    r"\b(impulso|anti[- ]?archivo|archiv(o|ar|ado)|indagaci[oó]n|reactivar|"
    r"inactividad|derecho\s+de\s+petici[oó]n\s+penal)\b",
    re.IGNORECASE,
)
_AUDIENCIA_RE = re.compile(r"\b(audiencia|interrogatorio|contrainterrogatorio|juicio|alegato)\b", re.IGNORECASE)
_CRONOLOGIA_RE = re.compile(r"\b(cronolog[ií]a|linea de tiempo|hechos|narrativa factual|relato)\b", re.IGNORECASE)


def classify_plan_template(message: str) -> PlanTemplateKind:
    """Prioriza flujos de alto volumen SPOA (VIF, querella, impulso) antes que genéricos."""
    text = message or ""
    if _TUTELA_RE.search(text):
        return "tutela"
    if _VIF_RE.search(text):
        return "vif_proteccion"
    if _QUERELLA_RE.search(text):
        return "querella_abreviado"
    if _IMPULSO_RE.search(text):
        return "indagacion_impulso"
    if _AUDIENCIA_RE.search(text):
        return "audiencia"
    if _CRONOLOGIA_RE.search(text):
        return "cronologia"
    return "generico"


def template_label(kind: PlanTemplateKind | str) -> str:
    if kind in _TEMPLATE_LABELS:
        return _TEMPLATE_LABELS[kind]  # type: ignore[index]
    return _TEMPLATE_LABELS["generico"]


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


def _append_chain(
    steps: list[PlanStep],
    order: int,
    chain: list[tuple[str, str, str]],
) -> int:
    """Añade pasos encadenados; cada uno depende del anterior."""
    for agent_id, title, user_summary in chain:
        dep = [steps[-1].step_id] if steps else []
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id=agent_id,
                title=title,
                user_summary=user_summary,
                depends_on=dep,
            )
        )
        order += 1
    return order


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
                "Como coordinador del expediente, identificaré la tarea, la etapa procesal "
                "aparente y pediré apoyo al equipo interno según esta plantilla."
            ),
        )
    )
    order += 1

    if kind == "cronologia":
        order = _append_chain(
            steps,
            order,
            [
                (
                    "analista_cronologia_hechos_penales",
                    "Construir cronología y matriz hecho-fuente",
                    "Voy a pedir al equipo interno que extraiga hechos, ordene la línea de tiempo "
                    "y señale vacíos o contradicciones que requieran verificación.",
                ),
                (
                    "analista_calidad_juridica",
                    "Control de calidad — cronología",
                    "Como coordinador, pediré al equipo de calidad revisar coherencia factual "
                    "y separación hecho/inferencia antes de entregarle el resultado.",
                ),
            ],
        )
    elif kind == "tutela":
        order = _append_chain(
            steps,
            order,
            [
                (
                    "evaluador_derechos_fundamentales_tutela",
                    "Evaluar procedencia y derecho fundamental",
                    "Voy a pedir al equipo constitucional analizar subsidiariedad, inmediatez "
                    "y el derecho fundamental presuntamente vulnerado.",
                ),
                (
                    "redactor_documentos_juridicos_penales",
                    "Borrador preliminar de tutela",
                    "Si procede, pediré al equipo de redacción un borrador con hechos, "
                    "fundamentos y pretensiones para su revisión.",
                ),
                (
                    "analista_calidad_juridica",
                    "Control de calidad — tutela",
                    "Como coordinador, pediré verificar tono, soporte normativo y riesgos "
                    "de improcedencia antes de entregarle el borrador.",
                ),
            ],
        )
    elif kind == "audiencia":
        order = _append_chain(
            steps,
            order,
            [
                (
                    "preparador_estrategico_audiencias_penales",
                    "Objetivo y estrategia de audiencia",
                    "Voy a pedir al equipo de audiencias definir objetivo procesal, "
                    "solicitudes orales y preguntas clave.",
                ),
                (
                    "analista_calidad_juridica",
                    "Checklist previo a audiencia",
                    "Como coordinador, pediré revisar riesgos procesales y coherencia "
                    "estratégica antes de la intervención.",
                ),
            ],
        )
    elif kind == "indagacion_impulso":
        order = _append_chain(
            steps,
            order,
            [
                (
                    "analista_cronologia_hechos_penales",
                    "Ordenar hechos para impulso en indagación",
                    "Voy a pedir al equipo de cronología consolidar hechos útiles para "
                    "reactivar o impulsar la noticia criminal.",
                ),
                (
                    "analista_tipicidad_y_responsabilidad_penal",
                    "Tipicidad preliminar del caso",
                    "Consultaré tipicidad y elementos del tipo para enfocar el impulso "
                    "sin afirmar conclusiones definitivas.",
                ),
                (
                    "analista_ruta_procesal_ley906",
                    "Ruta procesal y riesgo de archivo",
                    "Pediré al equipo de ruta 906 identificar etapa, oportunidades de "
                    "intervención y riesgos de archivo o inactividad.",
                ),
                (
                    "gestor_evidencia_y_soporte_probatorio",
                    "Brechas probatorias y recaudo",
                    "Voy a pedir inventario de evidencia y plan de recaudo para sostener "
                    "el impulso ante Fiscalía.",
                ),
                (
                    "redactor_documentos_juridicos_penales",
                    "Borrador de memorial o solicitud de impulso",
                    "Pediré al equipo de redacción el borrador revisable (memorial, "
                    "solicitud o derecho de petición penal).",
                ),
                (
                    "gestor_seguimiento_procesal_penal",
                    "Alertas de seguimiento post-impulso",
                    "Como coordinador, pediré alertas de radicado, términos y seguimiento "
                    "operativo tras el impulso.",
                ),
                (
                    "analista_calidad_juridica",
                    "Control de calidad — impulso",
                    "Pediré control de calidad sobre soporte fáctico, tono y pendientes "
                    "de verificación antes de entregarle la pieza.",
                ),
            ],
        )
    elif kind == "vif_proteccion":
        order = _append_chain(
            steps,
            order,
            [
                (
                    "analista_representacion_victimas",
                    "Teoría del caso y no revictimización",
                    "Voy a pedir al equipo de víctimas estructurar intereses, enfoque "
                    "diferencial y riesgos de revictimización.",
                ),
                (
                    "analista_tipicidad_y_responsabilidad_penal",
                    "Tipicidad VIF / familia",
                    "Consultaré tipicidad preliminar (p. ej. art. 229 C.P. u otras "
                    "conductas familiares) sin conclusiones definitivas.",
                ),
                (
                    "gestor_evidencia_y_soporte_probatorio",
                    "Soporte probatorio sensible",
                    "Pediré inventario de evidencia con cuidado de cadena de custodia "
                    "e intimidad de la víctima.",
                ),
                (
                    "preparador_estrategico_audiencias_penales",
                    "Solicitudes de protección (art. 134)",
                    "Voy a pedir preparación de solicitudes de atención/protección y "
                    "guion para control de garantías o juicio, según etapa.",
                ),
                (
                    "analista_calidad_juridica",
                    "Control de calidad — VIF",
                    "Como coordinador, pediré verificar confidencialidad, tono y "
                    "coherencia estratégica antes de entregarle la salida.",
                ),
            ],
        )
    elif kind == "querella_abreviado":
        order = _append_chain(
            steps,
            order,
            [
                (
                    "analista_ruta_procesal_ley906",
                    "Procedencia querella / abreviado",
                    "Voy a pedir al equipo de ruta 906 confirmar si el caso encaja en "
                    "querella o procedimiento abreviado (Ley 1826) y próximos pasos.",
                ),
                (
                    "analista_tipicidad_y_responsabilidad_penal",
                    "Tipicidad de la conducta querellable",
                    "Consultaré tipicidad preliminar para delimitar la pieza querellable.",
                ),
                (
                    "redactor_documentos_juridicos_penales",
                    "Borrador de querella o escrito abreviado",
                    "Pediré al equipo de redacción el borrador revisable para querella "
                    "o actuación en abreviado.",
                ),
                (
                    "gestor_seguimiento_procesal_penal",
                    "Seguimiento de audiencia concentrada",
                    "Como coordinador, pediré plan de seguimiento (términos, audiencia "
                    "concentrada y alertas operativas).",
                ),
            ],
        )

    if destination not in {s.agent_id for s in steps} and destination != "coordinador_expediente_penal":
        steps.append(
            _step(
                step_id=f"s{order:02d}",
                order=order,
                agent_id=destination,
                title=f"Consulta adicional — {desk_label(destination)}",
                user_summary=(
                    f"Como coordinador, pediré al equipo interno ({desk_label(destination)}) "
                    f"el análisis adicional que requiere su consulta."
                ),
                depends_on=[steps[-1].step_id],
            )
        )

    return steps
