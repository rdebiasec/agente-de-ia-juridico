"""Firma virtual penal-victimas — definición de agentes (OpenAI Agents SDK).

Arquitectura penal enfocada en representación de víctimas en Colombia:
un coordinador del expediente enruta a 10 especialistas por función
jurídica (cronología, tipicidad, ruta 906, víctimas, evidencia, audiencias,
redacción, seguimiento, tutela y control de calidad).
"""

from agents import Agent, handoff

from src.config import get_settings
from src.mcp.tools import get_knowledge_tools


def _load_system_prompt() -> str:
    settings = get_settings()
    path = settings.agente_dir / "prompts" / "sistema.md"
    return path.read_text(encoding="utf-8")


def _build_agent(name: str, rol_instructions: str, *, with_tools: bool = True) -> Agent:
    base = _load_system_prompt()
    instructions = f"{base}\n\n{rol_instructions.strip()}\n"
    kwargs: dict = {
        "name": name,
        "instructions": instructions,
        "model": get_settings().openai_model,
    }
    if with_tools:
        kwargs["tools"] = get_knowledge_tools()
    return Agent(**kwargs)


def build_analista_cronologia_hechos_penales_agent() -> Agent:
    return _build_agent(
        "analista_cronologia_hechos_penales",
        """
Rol: analista de cronología y hechos penales.
Misión: transformar relatos/documentos en línea de tiempo verificable,
identificar actores, contradicciones y vacíos fácticos.
No decides el fondo del caso ni inventas hechos; separa claramente:
hechos confirmados, narrados e inferidos.
""",
    )


def build_analista_tipicidad_y_responsabilidad_penal_agent() -> Agent:
    return _build_agent(
        "analista_tipicidad_y_responsabilidad_penal",
        """
Rol: penalista sustantivo.
Misión: analizar preliminarmente tipicidad, elementos del tipo, autoría,
participación, dolo/culpa, agravantes y riesgos de atipicidad.
No afirmes conclusiones definitivas ni inventes normas/jurisprudencia.
""",
    )


def build_analista_ruta_procesal_ley906_agent() -> Agent:
    return _build_agent(
        "analista_ruta_procesal_ley906",
        """
Rol: penalista procesal Ley 906.
Misión: identificar etapa procesal, oportunidades de intervención, términos
preliminares, riesgos procesales y ruta recomendada para la víctima.
No hagas seguimiento operativo diario (eso lo hace seguimiento procesal).
""",
    )


def build_analista_representacion_victimas_agent() -> Agent:
    return _build_agent(
        "analista_representacion_victimas",
        """
Rol: especialista en representación de víctimas.
Misión: construir teoría del caso desde derechos e intereses de la víctima,
evaluar daño/afectación, enfoque diferencial y riesgo de revictimización.
No prometas resultados judiciales ni uses lenguaje revictimizante.
""",
    )


def build_gestor_evidencia_y_soporte_probatorio_agent() -> Agent:
    return _build_agent(
        "gestor_evidencia_y_soporte_probatorio",
        """
Rol: gestor probatorio.
Misión: inventariar evidencia, construir matriz hecho-prueba, detectar brechas
y proponer plan de recaudo sin alterar ni manipular evidencia.
Cuando la evidencia requiera cadena de custodia estricta, marca escalamiento.
""",
    )


def build_preparador_estrategico_audiencias_penales_agent() -> Agent:
    return _build_agent(
        "preparador_estrategico_audiencias_penales",
        """
Rol: preparador de audiencias.
Misión: preparar objetivos, guiones, solicitudes, preguntas y checklist para
audiencias penales de representación de víctimas.
No reemplazas la intervención oral del abogado en audiencia.
""",
    )


def build_redactor_documentos_juridicos_penales_agent() -> Agent:
    return _build_agent(
        "redactor_documentos_juridicos_penales",
        """
Rol: redactor penal.
Misión: convertir análisis en borradores revisables (memoriales, solicitudes,
ampliaciones, derechos de petición, recursos preliminares y tutela preliminar).
No inventes hechos, citas, radicados ni anexos; marca pendientes de verificación.
""",
    )


def build_gestor_seguimiento_procesal_penal_agent() -> Agent:
    return _build_agent(
        "gestor_seguimiento_procesal_penal",
        """
Rol: dependiente judicial digital.
Misión: monitorear radicados, actuaciones, audiencias, términos operativos,
documentos pendientes e inactividad del caso.
Tu función es operativa; no sustituyes análisis jurídico estratégico.
""",
    )


def build_evaluador_derechos_fundamentales_tutela_agent() -> Agent:
    return _build_agent(
        "evaluador_derechos_fundamentales_tutela",
        """
Rol: analista constitucional.
Misión: evaluar derechos fundamentales y procedencia preliminar de tutela
en asuntos relacionados con el caso penal.
No conviertas todo en tutela; revisa subsidiariedad, inmediatez y riesgos.
""",
    )


def build_analista_calidad_juridica_agent() -> Agent:
    return _build_agent(
        "analista_calidad_juridica",
        """
Rol: revisor de calidad jurídica.
Misión: verificar soporte fáctico, citas normativas, consistencia estratégica,
confidencialidad y no revictimización antes de salida externa.
Nunca apruebes automáticamente sin marcar hallazgos y cambios requeridos.
""",
    )


def build_coordinador_agent() -> Agent:
    base = _load_system_prompt()
    instructions = f"""{base}

Eres el COORDINADOR DEL EXPEDIENTE PENAL del despacho.
Clasifica la consulta, identifica etapa aparente y enruta al especialista.
No inventes normas, sentencias, radicados ni hechos.
"""
    return Agent(
        name="coordinador_expediente_penal",
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_knowledge_tools(),
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


def build_orchestrator() -> Agent:
    base = _load_system_prompt()
    specialists = [builder() for builder in _SPECIALIST_BUILDERS]
    handoffs = [handoff(agent) for agent in specialists]
    instructions = f"""{base}

Eres el COORDINADOR DEL EXPEDIENTE PENAL del despacho.
Alcance único: representación de víctimas en contexto penal colombiano.

Enrutas cada consulta al especialista adecuado:
- Cronología y depuración factual -> analista_cronologia_hechos_penales
- Tipicidad y responsabilidad preliminar -> analista_tipicidad_y_responsabilidad_penal
- Etapa/ruta procesal Ley 906 -> analista_ruta_procesal_ley906
- Derechos/objetivos de la víctima -> analista_representacion_victimas
- Evidencia y brechas probatorias -> gestor_evidencia_y_soporte_probatorio
- Preparación de audiencias -> preparador_estrategico_audiencias_penales
- Redacción de piezas penales -> redactor_documentos_juridicos_penales
- Seguimiento operativo del caso -> gestor_seguimiento_procesal_penal
- Evaluación constitucional/tutela -> evaluador_derechos_fundamentales_tutela
- Control de calidad y trazabilidad -> analista_calidad_juridica

Si detectas un asunto fuera de penal-víctimas, acláralo explícitamente
y redirige la consulta al componente penal-víctimas.

Si faltan datos críticos (hechos, etapa, radicado, fuentes), solicítalos antes de
concluir. Mantén la conversación abierta hasta lograr un borrador útil y trazable.
No inventes normas, sentencias, radicados ni hechos.
"""
    return Agent(
        name="coordinador_expediente_penal",
        instructions=instructions,
        model=get_settings().openai_model,
        handoffs=handoffs,
        tools=get_knowledge_tools(),
    )
