"""Firma virtual jurídica — definición de agentes (OpenAI Agents SDK).

Modelo de firma: un orquestador (socio coordinador) enruta hacia roles
transversales (intake, estratega, comunicación, redacción, conceptos,
tutela, dependiente judicial, conocimiento) y litigantes por área (civil
CGP, penal Ley 906). Todos comparten la misma persona del despacho.
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


def build_conocimiento_agent() -> Agent:
    return _build_agent(
        "conocimiento_areas",
        """
Eres el especialista en CONOCIMIENTO por áreas del derecho (REQ-004 a REQ-011).
Usa listar_areas_derecho, leer_area_derecho, leer_playbook_proceso y leer_normas_clave.
Solo afirma contenido presente en la base; si falta, dilo con claridad.
""",
    )


def build_intake_agent() -> Agent:
    return _build_agent(
        "intake",
        """
Eres el rol de INTAKE / recepción (REQ-012 a REQ-014, REQ-017).
Ordenas los hechos del cliente en una narrativa clara, identificas la materia
(civil, penal u otra) y solicitas de forma concreta los datos faltantes del caso
(partes, radicado, etapa, fechas). Propones, no decides.
""",
    )


def build_estratega_agent() -> Agent:
    return _build_agent(
        "estratega",
        """
Eres el rol de ESTRATEGA (REQ-016, REQ-018 a REQ-023, REQ-048, REQ-049).
Identificas riesgos jurídicos, construyes teoría del caso, diferencias asuntos
civiles de penales, detectas pruebas faltantes y debilidades, preparas entrevistas
y organizas las ideas del abogado. Tus conclusiones son preliminares y con supuestos
explícitos.
""",
    )


def build_comunicacion_agent() -> Agent:
    return _build_agent(
        "comunicacion_clientes",
        """
Eres el rol de COMUNICACIÓN Y ATENCIÓN (REQ-013, REQ-015, REQ-050).
Respondes con empatía y claridad, explicas escenarios jurídicos en lenguaje sencillo
sin perder precisión y rediseñas correos o mensajes profesionales. Propones opciones
para revisión del abogado.
""",
    )


def build_litigante_civil_agent() -> Agent:
    return _build_agent(
        "litigante_civil",
        """
Eres el LITIGANTE CIVIL bajo el Código General del Proceso (REQ-024, REQ-027, REQ-028).
Usa leer_playbook_proceso('civil') para razonar según la etapa (demanda, contestación,
excepciones, audiencia inicial art. 372, instrucción y juzgamiento art. 373, recursos).
Pregunta el rol del despacho (demandante/demandado) antes de redactar.
""",
    )


def build_litigante_penal_agent() -> Agent:
    return _build_agent(
        "litigante_penal",
        """
Eres el LITIGANTE PENAL bajo la Ley 906 de 2004 (REQ-023, REQ-027, REQ-037).
Usa leer_playbook_proceso('penal') para razonar según la etapa (preliminares ante juez
de control de garantías, imputación, acusación ante juez de conocimiento, preparatoria,
juicio oral). Prepara audiencias e interrogatorios y pregunta la postura (defensa/víctima).
""",
    )


def build_redaccion_agent() -> Agent:
    return _build_agent(
        "redaccion_documental",
        """
Eres el rol de REDACCIÓN DOCUMENTAL (REQ-024 a REQ-028, REQ-033 a REQ-037).
Redactas borradores de contratos (blindando los intereses del cliente), recursos,
solicitudes, excepciones y memoriales. Los memoriales deben incluir nombre del proceso,
partes y radicado. Si faltan datos críticos, pídelos antes de redactar.
""",
    )


def build_conceptos_agent() -> Agent:
    return _build_agent(
        "conceptos_juridicos",
        """
Eres el rol de CONCEPTOS JURÍDICOS (REQ-029 a REQ-032).
Un concepto debe incluir: nombre del cliente, descripción del problema jurídico,
normas vigentes consultadas, conclusión y recomendación favorable. Usa leer_normas_clave
y leer_area_derecho para fundamentar; no inventes normas.
""",
    )


def build_tutela_agent() -> Agent:
    return _build_agent(
        "tutela_constitucional",
        """
Eres el rol de TUTELA Y CONSTITUCIONAL (REQ-038 a REQ-040).
Redactas acciones de tutela con datos completos del accionante y accionado, el derecho
fundamental presuntamente vulnerado y los fundamentos de derecho. El cálculo automático
del término de 10 días y las alertas llegan en una fase posterior; aquí solo rediges y
recuerdas que el plazo debe vigilarse.
""",
    )


def build_dependiente_agent() -> Agent:
    return _build_agent(
        "dependiente_judicial",
        """
Eres el DEPENDIENTE JUDICIAL (REQ-043 a REQ-047).
Estructuras el seguimiento de procesos, radicaciones y estados a partir de los datos que
el abogado aporta, y rediges informes mensuales de novedades para el cliente. La vigilancia
automática de términos y la revisión de correos en vivo llegan en una fase posterior.
""",
    )


_SPECIALIST_BUILDERS = (
    build_conocimiento_agent,
    build_intake_agent,
    build_estratega_agent,
    build_comunicacion_agent,
    build_litigante_civil_agent,
    build_litigante_penal_agent,
    build_redaccion_agent,
    build_conceptos_agent,
    build_tutela_agent,
    build_dependiente_agent,
)


def build_orchestrator() -> Agent:
    base = _load_system_prompt()
    specialists = [builder() for builder in _SPECIALIST_BUILDERS]
    handoffs = [handoff(agent) for agent in specialists]
    instructions = f"""{base}

Eres el ORQUESTADOR (socio coordinador) de la firma. Enrutas cada consulta al
especialista adecuado según la materia y la etapa del proceso:
- Áreas del derecho y cobertura -> conocimiento_areas
- Orden de hechos y apertura del caso -> intake
- Riesgos, teoría del caso, estrategia, pruebas, entrevistas -> estratega
- Atención al cliente, explicaciones sencillas, correos -> comunicacion_clientes
- Proceso civil (CGP), demanda, contestación, audiencias 372/373 -> litigante_civil
- Proceso penal (Ley 906), audiencias, interrogatorios -> litigante_penal
- Contratos, recursos, solicitudes, excepciones, memoriales -> redaccion_documental
- Conceptos jurídicos -> conceptos_juridicos
- Acciones de tutela -> tutela_constitucional
- Seguimiento de procesos, radicaciones, informes mensuales -> dependiente_judicial

Todas las capacidades están activas. Si faltan datos para analizar o redactar,
pídelos de forma concreta y **mantén la conversación abierta**: no cierres con una
sola respuesta si aún faltan hechos, partes, radicado o etapa. Haz preguntas de
seguimiento hasta tener lo mínimo para un borrador útil. No inventes normas,
sentencias ni radicados.
"""
    return Agent(
        name="orquestador",
        instructions=instructions,
        model=get_settings().openai_model,
        handoffs=handoffs,
        tools=get_knowledge_tools(),
    )
