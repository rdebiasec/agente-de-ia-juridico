"""Firma virtual penal-victimas — definición de agentes (OpenAI Agents SDK).

Arquitectura penal enfocada en representación de víctimas en Colombia:
un coordinador del expediente (POC) es el único interlocutor del abogado;
10 especialistas operan como backoffice interno (tools + trazas).
"""

from __future__ import annotations

from typing import Any

from agents import Agent, ModelSettings, RunContextWrapper

from src.agents.agent_cache import get_cached_agent, get_cached_orchestrator
from src.agents.prompt_assembly import assemble_instructions, instruction_stats
from src.agents.schemas import (
    BorradorDocumentoPenal,
    CronologiaPenal,
    DictamenCalidad,
    InventarioEvidencia,
    MatrizTipicidad,
    PreparacionAudiencia,
    RepresentacionVictimas,
    RutaProcesalLey906,
    SeguimientoProcesal,
    Tutela,
)
from src.agents.sdk_guardrails import (
    calidad_output_guardrails,
    poc_input_guardrails,
    poc_output_guardrails,
    poc_tool_input_guardrails,
    poc_tool_output_guardrails,
    redactor_output_guardrails,
    specialist_output_guardrails,
    tutela_output_guardrails,
)
from src.agents.skill_catalog import (
    HIGH_RISK_AGENTS,
    agent_capability_anchor,
)
from src.agents.specialist_consult import SpecialistConsultInput, specialist_input_builder
from src.agents.structured_render import render_structured_output
from src.config import get_settings
from src.mcp.tools import get_knowledge_tools

POC_AGENT_ID = "coordinador_expediente_penal"

_BACKOFFICE_VOICE = """
Modo BACKOFFICE (equipo interno):
- No saludas al abogado ni te presentas como interlocutor ("yo soy el analista…").
- No firmas la respuesta como cara del despacho.
- Devuelves hallazgos operativos para el coordinador: hechos, riesgos, borrador interno,
  pendientes de verificación y recomendaciones accionables.
- El coordinador sintetiza y responde al abogado con una sola voz.
"""

# Contratos as_tool: skill primario + cuándo usar / no usar (routing L10).
_SPECIALIST_TOOL_DESCRIPTIONS: dict[str, str] = {
    "analista_cronologia_hechos_penales": (
        "Cronología y hechos (skill: construir_cronologia_penal). "
        "Usar para línea de tiempo, actores, contradicciones y vacíos fácticos. "
        "No usar para tipicidad, redacción de memoriales ni tutela."
    ),
    "analista_tipicidad_y_responsabilidad_penal": (
        "Tipicidad y responsabilidad (skill: descomponer_elementos_tipo_penal). "
        "Usar para elementos del tipo, autoría, dolo/culpa, agravantes y riesgo de atipicidad. "
        "No usar para inventariar pruebas ni redactar memoriales."
    ),
    "analista_ruta_procesal_ley906": (
        "Ruta procesal Ley 906 (skill: identificar_etapa_procesal_ley906). "
        "Usar para etapa, oportunidades de intervención, términos y riesgos procesales. "
        "No usar para redacción de tutela ni inventario de evidencia."
    ),
    "analista_representacion_victimas": (
        "Representación de víctimas (skill: construir_teoria_caso_victima). "
        "Usar para teoría del caso, derechos, daño/afectación, enfoque diferencial y no revictimización. "
        "No usar para tipicidad pura ni seguimiento de radicados."
    ),
    "gestor_evidencia_y_soporte_probatorio": (
        "Evidencia y soporte probatorio (skill: inventariar_evidencia). "
        "Usar para inventario, matriz hecho-prueba, brechas y plan de recaudo. "
        "No usar para redactar memoriales ni evaluar tutela."
    ),
    "preparador_estrategico_audiencias_penales": (
        "Audiencias penales (skill: preparar_preguntas_audiencia). "
        "Usar para objetivos, guiones, solicitudes orales, preguntas y checklist de audiencia. "
        "No usar para memorial escrito ni tipicidad aislada."
    ),
    "redactor_documentos_juridicos_penales": (
        "Redacción jurídica penal (skill: redactar_memorial_penal). "
        "Usar para borradores internos: memoriales, solicitudes, ampliaciones o derecho de petición. "
        "No usar para tutela constitucional (derivar a evaluador_tutela) ni dictamen de calidad."
    ),
    "gestor_seguimiento_procesal_penal": (
        "Seguimiento procesal (skill: monitorear_radicado). "
        "Usar para radicados, actuaciones, audiencias calendarizadas, términos e inactividad. "
        "No usar para redactar memoriales ni tipicidad."
    ),
    "evaluador_derechos_fundamentales_tutela": (
        "Derechos fundamentales / tutela (skill: evaluar_procedencia_tutela). "
        "Usar para procedencia preliminar de tutela vinculada al caso penal. "
        "No usar para memorial ordinario ni inventario de evidencia."
    ),
    "analista_calidad_juridica": (
        "Calidad jurídica (skill: revisar_coherencia_estrategica). "
        "Usar para soporte fáctico, citas, coherencia, confidencialidad y no revictimización. "
        "Devuelve DictamenCalidad. No usar para redactar el memorial final."
    ),
}

# Alineado a HIGH_RISK_AGENTS: needs_approval en chat cuando require_tool_approval=True.
_APPROVAL_REQUIRED_TOOLS = frozenset(HIGH_RISK_AGENTS)
APPROVAL_REQUIRED_TOOL_IDS = _APPROVAL_REQUIRED_TOOLS

# Vecinos tipicos: destino inferido + 1–2 adyacentes (superficie dinamica).
_SPECIALIST_NEIGHBORS: dict[str, frozenset[str]] = {
    "analista_cronologia_hechos_penales": frozenset(
        {
            "gestor_evidencia_y_soporte_probatorio",
            "analista_calidad_juridica",
            "analista_tipicidad_y_responsabilidad_penal",
            "analista_ruta_procesal_ley906",  # G04: hechos ↔ etapa
        }
    ),
    "analista_tipicidad_y_responsabilidad_penal": frozenset(
        {
            "gestor_evidencia_y_soporte_probatorio",
            "analista_calidad_juridica",
            "analista_cronologia_hechos_penales",
            "analista_ruta_procesal_ley906",  # G04
        }
    ),
    "analista_ruta_procesal_ley906": frozenset(
        {
            "gestor_seguimiento_procesal_penal",
            "preparador_estrategico_audiencias_penales",
            "analista_calidad_juridica",
        }
    ),
    "analista_representacion_victimas": frozenset(
        {
            "analista_cronologia_hechos_penales",
            "analista_calidad_juridica",
            "evaluador_derechos_fundamentales_tutela",
        }
    ),
    "gestor_evidencia_y_soporte_probatorio": frozenset(
        {
            "analista_cronologia_hechos_penales",
            "analista_tipicidad_y_responsabilidad_penal",
            "analista_calidad_juridica",
        }
    ),
    "preparador_estrategico_audiencias_penales": frozenset(
        {
            "analista_ruta_procesal_ley906",
            "analista_representacion_victimas",
            "analista_calidad_juridica",
        }
    ),
    "gestor_seguimiento_procesal_penal": frozenset(
        {
            "analista_ruta_procesal_ley906",
            "analista_calidad_juridica",
        }
    ),
    "analista_calidad_juridica": frozenset(
        {
            "analista_cronologia_hechos_penales",
            "analista_ruta_procesal_ley906",
        }
    ),
    "redactor_documentos_juridicos_penales": frozenset(
        {
            "analista_calidad_juridica",
            "analista_ruta_procesal_ley906",
        }
    ),
    "evaluador_derechos_fundamentales_tutela": frozenset(
        {
            "analista_calidad_juridica",
            "analista_ruta_procesal_ley906",
            "analista_representacion_victimas",
        }
    ),
}

# Overrides por costo/complejidad; techo duro evita loops caros (L10).
_NESTED_MAX_TURNS_BY_AGENT: dict[str, int] = {
    "analista_calidad_juridica": 4,
    "redactor_documentos_juridicos_penales": 5,
    "preparador_estrategico_audiencias_penales": 5,
    "evaluador_derechos_fundamentales_tutela": 4,
    "gestor_evidencia_y_soporte_probatorio": 4,
}
_NESTED_MAX_TURNS_CEILING = 8


def _model_for_agent(agent_id: str) -> str:
    """Modelo por criticidad: alto riesgo usa openai_model_high_risk (Ch2 selection)."""
    settings = get_settings()
    if agent_id in HIGH_RISK_AGENTS:
        return settings.openai_model_high_risk or settings.openai_model
    return settings.openai_model


def _model_settings_for_agent(agent_id: str) -> ModelSettings:
    """Temperatura baja en todos; high-risk aún más determinista (Opción A / B01)."""
    settings = get_settings()
    temp = (
        settings.agent_temperature_high_risk
        if agent_id in HIGH_RISK_AGENTS
        else settings.agent_temperature
    )
    return ModelSettings(temperature=float(temp))


def _capability_anchor(agent_id: str) -> str:
    return agent_capability_anchor(agent_id)


def _specialist_knowledge_tools():
    """Plan/especialistas: lecturas MD + listar_areas habilitados (no chat Gerente slim).

    El chat del POC sigue con include_full_reads=False / include_list_areas=False
    (ver build_orchestrator / runner). Aquí el especialista puede grounding profundo
    sin volcar dumps al abogado.
    """
    return get_knowledge_tools(
        include_kb_search=True,
        include_full_reads=True,
        include_list_areas=True,
    )


def _build_agent(
    name: str,
    *,
    with_tools: bool = True,
    slim: bool = True,
    output_type: type | None = None,
    output_guardrails: list | None = None,
) -> Agent:
    instructions = assemble_instructions(
        name,
        slim=slim,
        backoffice=True,
        backoffice_voice=_BACKOFFICE_VOICE,
        capability_anchor=_capability_anchor(name),
    )
    kwargs: dict = {
        "name": name,
        "instructions": instructions,
        "model": _model_for_agent(name),
        "model_settings": _model_settings_for_agent(name),
        "output_guardrails": output_guardrails or specialist_output_guardrails(),
    }
    if with_tools:
        kwargs["tools"] = _specialist_knowledge_tools()
    if output_type is not None:
        kwargs["output_type"] = output_type
    return Agent(**kwargs)


def build_analista_cronologia_hechos_penales_agent() -> Agent:
    return _build_agent(
        "analista_cronologia_hechos_penales",
        output_type=CronologiaPenal,
    )


def build_analista_tipicidad_y_responsabilidad_penal_agent() -> Agent:
    return _build_agent(
        "analista_tipicidad_y_responsabilidad_penal",
        output_type=MatrizTipicidad,
    )


def build_analista_ruta_procesal_ley906_agent() -> Agent:
    return _build_agent(
        "analista_ruta_procesal_ley906",
        output_type=RutaProcesalLey906,
    )


def build_analista_representacion_victimas_agent() -> Agent:
    return _build_agent(
        "analista_representacion_victimas",
        output_type=RepresentacionVictimas,
    )


def build_gestor_evidencia_y_soporte_probatorio_agent() -> Agent:
    return _build_agent(
        "gestor_evidencia_y_soporte_probatorio",
        output_type=InventarioEvidencia,
    )


def build_preparador_estrategico_audiencias_penales_agent() -> Agent:
    return _build_agent(
        "preparador_estrategico_audiencias_penales",
        output_type=PreparacionAudiencia,
    )


def build_redactor_documentos_juridicos_penales_agent() -> Agent:
    return _build_agent(
        "redactor_documentos_juridicos_penales",
        output_type=BorradorDocumentoPenal,
        output_guardrails=redactor_output_guardrails(),
    )


def build_gestor_seguimiento_procesal_penal_agent() -> Agent:
    return _build_agent(
        "gestor_seguimiento_procesal_penal",
        output_type=SeguimientoProcesal,
    )


def build_evaluador_derechos_fundamentales_tutela_agent() -> Agent:
    return _build_agent(
        "evaluador_derechos_fundamentales_tutela",
        output_type=Tutela,
        output_guardrails=tutela_output_guardrails(),
    )


def build_analista_calidad_juridica_agent() -> Agent:
    return _build_agent(
        "analista_calidad_juridica",
        output_type=DictamenCalidad,
        output_guardrails=calidad_output_guardrails(),
    )


def build_coordinador_agent(*, slim_instructions: bool = True) -> Agent:
    """POC sin especialistas (pasos de plan / consultas directas al coordinador)."""
    instructions = assemble_instructions(
        POC_AGENT_ID,
        slim=slim_instructions,
        backoffice=False,
        capability_anchor=_capability_anchor(POC_AGENT_ID),
    )
    return Agent(
        name=POC_AGENT_ID,
        instructions=instructions,
        model=_model_for_agent(POC_AGENT_ID),
        model_settings=_model_settings_for_agent(POC_AGENT_ID),
        tools=get_knowledge_tools(
            include_kb_search=True,
            include_full_reads=False,
            include_list_areas=False,
        ),
        input_guardrails=poc_input_guardrails(),
        output_guardrails=poc_output_guardrails(),
    )


_AGENT_BUILDERS: dict[str, object] = {
    "coordinador_expediente_penal": build_coordinador_agent,
    "analista_cronologia_hechos_penales": build_analista_cronologia_hechos_penales_agent,
    "analista_tipicidad_y_responsabilidad_penal": build_analista_tipicidad_y_responsabilidad_penal_agent,
    "analista_ruta_procesal_ley906": build_analista_ruta_procesal_ley906_agent,
    "analista_representacion_victimas": build_analista_representacion_victimas_agent,
    "gestor_evidencia_y_soporte_probatorio": build_gestor_evidencia_y_soporte_probatorio_agent,
    "preparador_estrategico_audiencias_penales": build_preparador_estrategico_audiencias_penales_agent,
    "redactor_documentos_juridicos_penales": build_redactor_documentos_juridicos_penales_agent,
    "gestor_seguimiento_procesal_penal": build_gestor_seguimiento_procesal_penal_agent,
    "evaluador_derechos_fundamentales_tutela": build_evaluador_derechos_fundamentales_tutela_agent,
    "analista_calidad_juridica": build_analista_calidad_juridica_agent,
}


def get_agent_by_id(agent_id: str) -> Agent | None:
    builder = _AGENT_BUILDERS.get(agent_id)
    if builder is None:
        return None
    return get_cached_agent(agent_id, builder)  # type: ignore[arg-type]


_SPECIALIST_BUILDERS = (
    build_analista_cronologia_hechos_penales_agent,
    build_analista_tipicidad_y_responsabilidad_penal_agent,
    build_analista_ruta_procesal_ley906_agent,
    build_analista_representacion_victimas_agent,
    build_gestor_evidencia_y_soporte_probatorio_agent,
    build_preparador_estrategico_audiencias_penales_agent,
    build_redactor_documentos_juridicos_penales_agent,
    build_gestor_seguimiento_procesal_penal_agent,
    build_evaluador_derechos_fundamentales_tutela_agent,
    build_analista_calidad_juridica_agent,
)

SPECIALIST_AGENT_IDS = frozenset(_SPECIALIST_TOOL_DESCRIPTIONS.keys())


def nested_max_turns_for(agent_id: str) -> int:
    """Tope de turnos del especialista invocado via as_tool (con techo duro)."""
    override = _NESTED_MAX_TURNS_BY_AGENT.get(agent_id)
    base = override if override is not None else get_settings().agent_nested_max_turns
    try:
        turns = int(base)
    except (TypeError, ValueError):
        turns = 3
    return max(1, min(turns, _NESTED_MAX_TURNS_CEILING))


def enabled_specialists_for_focus(
    focus_agent_id: str | None,
    available: frozenset[str] | set[str],
) -> frozenset[str]:
    """Especialistas visibles al LLM: destino + vecinos; todos si el foco es el POC."""
    available_set = frozenset(available)
    if not focus_agent_id or focus_agent_id == POC_AGENT_ID:
        return available_set
    chosen = {focus_agent_id}
    chosen |= set(_SPECIALIST_NEIGHBORS.get(focus_agent_id, frozenset()))
    if "analista_calidad_juridica" in available_set:
        chosen.add("analista_calidad_juridica")
    return frozenset(name for name in chosen if name in available_set)


def _as_tool_failure_code(error: Exception) -> str:
    """Código estable para soporte/trazas (sin stack ni PII)."""
    from agents.exceptions import (
        MaxTurnsExceeded,
        ModelBehaviorError,
        ModelRefusalError,
        ToolTimeoutError,
        UserError,
    )

    from src.agents.runner import AgentBudgetExceeded

    if isinstance(error, AgentBudgetExceeded):
        return "budget_exceeded"
    if isinstance(error, MaxTurnsExceeded):
        return "max_turns"
    if isinstance(error, ToolTimeoutError):
        return "tool_timeout"
    if isinstance(error, ModelRefusalError):
        return "model_refusal"
    if isinstance(error, ModelBehaviorError):
        return "model_behavior"
    if isinstance(error, UserError):
        return "user_error"
    if type(error).__name__ == "ValidationError":
        return "invalid_input"
    if type(error).__name__ in {"TimeoutError", "asyncio.TimeoutError"} or isinstance(
        error, TimeoutError
    ):
        return "timeout"
    return f"error:{type(error).__name__}"


def _as_tool_failure_error(
    ctx: RunContextWrapper[Any],  # noqa: ARG001
    error: Exception,
) -> str:
    """Re-lanza presupuestos/tripwires; mensajes tipados y sanitizados para el resto."""
    from agents import InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
    from agents.exceptions import (
        ToolInputGuardrailTripwireTriggered,
        ToolOutputGuardrailTripwireTriggered,
    )

    from src.agents.runner import AgentBudgetExceeded

    if isinstance(
        error,
        (
            AgentBudgetExceeded,
            InputGuardrailTripwireTriggered,
            OutputGuardrailTripwireTriggered,
            ToolInputGuardrailTripwireTriggered,
            ToolOutputGuardrailTripwireTriggered,
        ),
    ):
        raise error

    code = _as_tool_failure_code(error)
    hints = {
        "max_turns": "El especialista agotó sus turnos internos. Acote el pedido o apruebe un plan.",
        "tool_timeout": "La consulta interna superó el tiempo límite. Reintente con un pedido más corto.",
        "timeout": "La consulta interna superó el tiempo límite. Reintente con un pedido más corto.",
        "model_refusal": "El modelo rechazó la consulta interna. Reformule sin pedir datos sensibles innecesarios.",
        "model_behavior": "Salida inválida del especialista. Reformule el pedido con hechos confirmados.",
        "invalid_input": "Pedido al especialista mal formado. Envíe pedido concreto y hechos confirmados.",
        "user_error": "Configuración inválida de la consulta interna. Revise el pedido o el plan.",
        "budget_exceeded": "Presupuesto de ejecución agotado. Apruebe un plan o reduzca el alcance.",
    }
    detail = hints.get(
        code,
        f"El especialista interno no pudo completar la consulta ({code}). "
        "Reformule el pedido o apruebe un plan.",
    )
    return detail


async def _tool_output_text(result: object) -> str:
    output = getattr(result, "final_output", result)
    return render_structured_output(output)


def build_orchestrator(
    *,
    require_tool_approval: bool = True,
    include_high_risk_tools: bool = True,
    focus_agent_id: str | None = None,
    include_kb_search_tool: bool = True,
    include_full_read_tools: bool = False,
    include_list_areas_tool: bool = False,
    slim_instructions: bool = True,
    use_cache: bool = True,
) -> Agent:
    """POC coordinador con especialistas como tools internas (no handoffs terminales).

    Política de tools de conocimiento:
    - Chat Gerente: full_reads/list_areas off (defaults) — respuesta slim.
    - Quien construya orquestador para plan puede pasar include_full_read_tools=True
      e include_list_areas_tool=True; los especialistas standalone ya las traen.
    """
    if use_cache:
        return get_cached_orchestrator(
            build_orchestrator,
            require_tool_approval=require_tool_approval,
            include_high_risk_tools=include_high_risk_tools,
            focus_agent_id=focus_agent_id,
            include_kb_search_tool=include_kb_search_tool,
            include_full_read_tools=include_full_read_tools,
            slim_instructions=slim_instructions,
            include_list_areas_tool=include_list_areas_tool,
        )

    instructions = assemble_instructions(
        POC_AGENT_ID,
        slim=slim_instructions,
        backoffice=False,
        capability_anchor=_capability_anchor(POC_AGENT_ID),
    )
    specialists = [builder() for builder in _SPECIALIST_BUILDERS]
    if not include_high_risk_tools:
        specialists = [
            agent for agent in specialists if agent.name not in _APPROVAL_REQUIRED_TOOLS
        ]
    available_ids = frozenset(agent.name for agent in specialists)
    enabled_ids = enabled_specialists_for_focus(focus_agent_id, available_ids)

    specialist_tools = []
    for agent in specialists:
        turns = nested_max_turns_for(agent.name)
        tool = agent.as_tool(
            tool_name=agent.name,
            tool_description=_SPECIALIST_TOOL_DESCRIPTIONS.get(
                agent.name,
                f"Consulta interna al equipo {agent.name}.",
            ),
            custom_output_extractor=_tool_output_text,
            needs_approval=require_tool_approval
            and agent.name in _APPROVAL_REQUIRED_TOOLS,
            # bool (no callable): evals/tests leen is_enabled como flag; vecinos amplían superficie.
            is_enabled=agent.name in enabled_ids,
            max_turns=turns,
            parameters=SpecialistConsultInput,
            input_builder=specialist_input_builder,
            include_input_schema=False,
            failure_error_function=_as_tool_failure_error,
        )
        tool.tool_input_guardrails = poc_tool_input_guardrails()
        tool.tool_output_guardrails = poc_tool_output_guardrails()
        tool.nested_max_turns = turns  # type: ignore[attr-defined]
        specialist_tools.append(tool)

    knowledge = get_knowledge_tools(
        include_kb_search=include_kb_search_tool,
        include_full_reads=include_full_read_tools,
        include_list_areas=include_list_areas_tool,
    )
    agent = Agent(
        name=POC_AGENT_ID,
        instructions=instructions,
        model=_model_for_agent(POC_AGENT_ID),
        model_settings=_model_settings_for_agent(POC_AGENT_ID),
        tools=[*knowledge, *specialist_tools],
        input_guardrails=poc_input_guardrails(),
        output_guardrails=poc_output_guardrails(),
    )
    agent.instruction_stats = instruction_stats(instructions)  # type: ignore[attr-defined]
    return agent


# Compat: tests / código legacy que importaban _policy_block
def _policy_block(agent_id: str | None = None) -> str:  # noqa: D401
    from src.agents.prompt_assembly import full_policy_block, slim_policy_block

    if agent_id is None:
        return slim_policy_block()
    return full_policy_block(agent_id)
