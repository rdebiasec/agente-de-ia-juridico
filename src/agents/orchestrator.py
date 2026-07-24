"""Firma virtual penal-victimas — definición de agentes (OpenAI Agents SDK).

Arquitectura penal enfocada en representación de víctimas en Colombia:
un coordinador del expediente (POC) es el único interlocutor del abogado;
10 especialistas operan como backoffice interno (tools + trazas).
"""

from agents import Agent

from src.agents.schemas import BorradorDocumentoPenal
from src.agents.sdk_guardrails import poc_input_guardrails, poc_output_guardrails
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

_SPECIALIST_TOOL_DESCRIPTIONS: dict[str, str] = {
    "analista_cronologia_hechos_penales": (
        "Consulta interna al equipo de cronología y hechos penales: línea de tiempo, "
        "actores, contradicciones y vacíos fácticos."
    ),
    "analista_tipicidad_y_responsabilidad_penal": (
        "Consulta interna al equipo de tipicidad y responsabilidad penal: elementos del tipo, "
        "autoría, dolo/culpa, agravantes y riesgos de atipicidad."
    ),
    "analista_ruta_procesal_ley906": (
        "Consulta interna al equipo de ruta procesal Ley 906: etapa, oportunidades de "
        "intervención, términos preliminares y riesgos procesales."
    ),
    "analista_representacion_victimas": (
        "Consulta interna al equipo de representación de víctimas: teoría del caso, "
        "derechos, daño/afectación, enfoque diferencial y no revictimización."
    ),
    "gestor_evidencia_y_soporte_probatorio": (
        "Consulta interna al equipo probatorio: inventario de evidencia, matriz hecho-prueba, "
        "brechas y plan de recaudo."
    ),
    "preparador_estrategico_audiencias_penales": (
        "Consulta interna al equipo de audiencias: objetivos, guiones, solicitudes, "
        "preguntas y checklist para representación de víctimas."
    ),
    "redactor_documentos_juridicos_penales": (
        "Consulta interna al equipo de redacción: borradores internos de memoriales, "
        "solicitudes, ampliaciones, derechos de petición o tutela preliminar."
    ),
    "gestor_seguimiento_procesal_penal": (
        "Consulta interna al equipo de seguimiento procesal: radicados, actuaciones, "
        "audiencias, términos e inactividad."
    ),
    "evaluador_derechos_fundamentales_tutela": (
        "Consulta interna al equipo constitucional: derechos fundamentales y procedencia "
        "preliminar de tutela vinculada al caso penal."
    ),
    "analista_calidad_juridica": (
        "Consulta interna al equipo de calidad jurídica: soporte fáctico, citas, coherencia "
        "estratégica, confidencialidad y no revictimización."
    ),
}


def _load_system_prompt() -> str:
    from src.config_store import load_prompt_text

    try:
        return load_prompt_text("sistema")
    except Exception:
        path = get_settings().agente_dir / "prompts" / "sistema.md"
        return path.read_text(encoding="utf-8")


def _load_agent_prompt(agent_id: str) -> str:
    from src.config_store import load_prompt_text

    try:
        return load_prompt_text(agent_id).strip()
    except Exception:
        path = get_settings().agente_dir / "prompts" / "agents" / f"{agent_id}.md"
        return path.read_text(encoding="utf-8").strip()


def _policy_block() -> str:
    """Políticas de guardrail editables (texto) inyectadas en instrucciones."""
    try:
        from src.config_store import load_guardrail_policies

        policies = load_guardrail_policies()
    except Exception:
        return ""
    if not policies:
        return ""
    lines = ["Políticas obligatorias del despacho (guardrails de política):"]
    for g in policies:
        lines.append(f"- [{g['id']}] {g['name']}: {g['desc']}")
    return "\n".join(lines)


def _build_agent(name: str, *, with_tools: bool = True) -> Agent:
    base = _load_system_prompt()
    rol = _load_agent_prompt(name)
    policy = _policy_block()
    parts = [base, rol, _BACKOFFICE_VOICE.strip()]
    if policy:
        parts.append(policy)
    instructions = "\n\n".join(parts) + "\n"
    kwargs: dict = {
        "name": name,
        "instructions": instructions,
        "model": get_settings().openai_model,
    }
    if with_tools:
        kwargs["tools"] = get_knowledge_tools()
    return Agent(**kwargs)


def build_analista_cronologia_hechos_penales_agent() -> Agent:
    return _build_agent("analista_cronologia_hechos_penales")


def build_analista_tipicidad_y_responsabilidad_penal_agent() -> Agent:
    return _build_agent("analista_tipicidad_y_responsabilidad_penal")


def build_analista_ruta_procesal_ley906_agent() -> Agent:
    return _build_agent("analista_ruta_procesal_ley906")


def build_analista_representacion_victimas_agent() -> Agent:
    return _build_agent("analista_representacion_victimas")


def build_gestor_evidencia_y_soporte_probatorio_agent() -> Agent:
    return _build_agent("gestor_evidencia_y_soporte_probatorio")


def build_preparador_estrategico_audiencias_penales_agent() -> Agent:
    return _build_agent("preparador_estrategico_audiencias_penales")


def build_redactor_documentos_juridicos_penales_agent() -> Agent:
    base = _load_system_prompt()
    rol = _load_agent_prompt("redactor_documentos_juridicos_penales")
    policy = _policy_block()
    parts = [base, rol, _BACKOFFICE_VOICE.strip()]
    if policy:
        parts.append(policy)
    instructions = "\n\n".join(parts) + "\n"
    return Agent(
        name="redactor_documentos_juridicos_penales",
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_knowledge_tools(),
        output_type=BorradorDocumentoPenal,
    )


def build_gestor_seguimiento_procesal_penal_agent() -> Agent:
    return _build_agent("gestor_seguimiento_procesal_penal")


def build_evaluador_derechos_fundamentales_tutela_agent() -> Agent:
    return _build_agent("evaluador_derechos_fundamentales_tutela")


def build_analista_calidad_juridica_agent() -> Agent:
    return _build_agent("analista_calidad_juridica")


def build_coordinador_agent() -> Agent:
    """POC sin especialistas (pasos de plan / consultas directas al coordinador)."""
    base = _load_system_prompt()
    rol = _load_agent_prompt(POC_AGENT_ID)
    policy = _policy_block()
    parts = [base, rol]
    if policy:
        parts.append(policy)
    instructions = "\n\n".join(parts) + "\n"
    return Agent(
        name=POC_AGENT_ID,
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_knowledge_tools(),
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
    return builder()  # type: ignore[operator]


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


def build_orchestrator() -> Agent:
    """POC coordinador con especialistas como tools internas (no handoffs terminales)."""
    base = _load_system_prompt()
    rol = _load_agent_prompt(POC_AGENT_ID)
    policy = _policy_block()
    specialists = [builder() for builder in _SPECIALIST_BUILDERS]

    async def _tool_output_text(result: object) -> str:
        output = getattr(result, "final_output", result)
        if output is None:
            return ""
        if isinstance(output, str):
            return output
        if hasattr(output, "model_dump"):
            data = output.model_dump()
            cuerpo = data.get("cuerpo")
            if isinstance(cuerpo, str) and cuerpo.strip():
                titulo = str(data.get("titulo") or "").strip()
                pendientes = data.get("pendientes_verificacion") or []
                header = f"{titulo}\n\n" if titulo else ""
                extras = ""
                if pendientes:
                    extras = "\n\nPendientes de verificación:\n- " + "\n- ".join(
                        str(p) for p in pendientes
                    )
                return f"{header}{cuerpo}{extras}".strip()
            return str(data)
        return str(output)

    specialist_tools = [
        agent.as_tool(
            tool_name=agent.name,
            tool_description=_SPECIALIST_TOOL_DESCRIPTIONS.get(
                agent.name,
                f"Consulta interna al equipo {agent.name}.",
            ),
            custom_output_extractor=_tool_output_text,
        )
        for agent in specialists
    ]
    parts = [base, rol]
    if policy:
        parts.append(policy)
    instructions = "\n\n".join(parts) + "\n"
    return Agent(
        name=POC_AGENT_ID,
        instructions=instructions,
        model=get_settings().openai_model,
        tools=[*get_knowledge_tools(), *specialist_tools],
        input_guardrails=poc_input_guardrails(),
        output_guardrails=poc_output_guardrails(),
    )
