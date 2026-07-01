"""Firma virtual jurídica — definición de agentes (OpenAI Agents SDK)."""

from agents import Agent, handoff

from src.agents.agent_names import (
    AGENTE_CONCEPTOS_JURIDICOS,
    AGENTE_CONOCIMIENTO_DERECHO,
    AGENTE_COORDINADOR_CIVIL,
    AGENTE_COORDINADOR_PENAL,
    AGENTE_COORDINADOR_PRINCIPAL,
    AGENTE_ESTRATEGIA_CASOS,
    AGENTE_RECEPCIONISTA,
    AGENTE_REDACTION_DOCUMENTAL,
    AGENTE_SEGUIMIENTO_PROCESAL,
    AGENTE_SERVICIO_CLIENTE,
    AGENTE_TUTELA_CONSTITUCIONAL,
)
from src.agents.system_prompt import load_system_prompt
from src.config import get_settings
from src.mcp.tools import get_knowledge_tools


def _build_agent(name: str, rol_instructions: str, *, with_tools: bool = True) -> Agent:
    base = load_system_prompt()
    instructions = f"{base}\n\n{rol_instructions.strip()}\n"
    kwargs: dict = {
        "name": name,
        "instructions": instructions,
        "model": get_settings().openai_model,
    }
    if with_tools:
        kwargs["tools"] = get_knowledge_tools()
    return Agent(**kwargs)


def build_agente_conocimiento_derecho() -> Agent:
    return _build_agent(
        AGENTE_CONOCIMIENTO_DERECHO,
        """
Eres el especialista en CONOCIMIENTO DEL DERECHO (REQ-004 a REQ-011).
Usa listar_areas_derecho, leer_area_derecho, leer_playbook_proceso y leer_normas_clave.
Solo afirma contenido presente en la base; si falta, dilo con claridad.
""",
    )


def build_agente_recepcionista() -> Agent:
    return _build_agent(
        AGENTE_RECEPCIONISTA,
        """
Eres el RECEPCIONISTA (REQ-012 a REQ-014, REQ-017).
Ordenas los hechos del cliente en una narrativa clara, identificas la materia
(civil, penal u otra) y solicitas de forma concreta los datos faltantes del caso
(partes, radicado, etapa, fechas). Propones, no decides.
""",
    )


def build_agente_estrategia_casos() -> Agent:
    return _build_agent(
        AGENTE_ESTRATEGIA_CASOS,
        """
Eres ESTRATEGIA DE CASOS (REQ-016, REQ-018 a REQ-023, REQ-048, REQ-049).
Identificas riesgos jurídicos, construyes teoría del caso, diferencias asuntos
civiles de penales, detectas pruebas faltantes y debilidades, preparas entrevistas
y organizas las ideas del abogado. Tus conclusiones son preliminares y con supuestos
explícitos.
""",
    )


def build_agente_servicio_cliente() -> Agent:
    return _build_agent(
        AGENTE_SERVICIO_CLIENTE,
        """
Eres SERVICIO AL CLIENTE (REQ-013, REQ-015, REQ-050).
Respondes con empatía y claridad, explicas escenarios jurídicos en lenguaje sencillo
sin perder precisión y rediseñas correos o mensajes profesionales. Propones opciones
para revisión del abogado.
""",
    )


def build_agente_coordinador_civil() -> Agent:
    from src.agents.civil_orchestrator import build_agente_coordinador_civil

    return build_agente_coordinador_civil()


def build_agente_coordinador_penal() -> Agent:
    from src.agents.penal_orchestrator import build_agente_coordinador_penal

    return build_agente_coordinador_penal()


def build_agente_redaccion_documental() -> Agent:
    return _build_agent(
        AGENTE_REDACTION_DOCUMENTAL,
        """
Eres REDACCIÓN DOCUMENTAL (REQ-024 a REQ-028, REQ-033 a REQ-037).
Redactas borradores de contratos (blindando los intereses del cliente), recursos,
solicitudes, excepciones y memoriales. Los memoriales deben incluir nombre del proceso,
partes y radicado. Si faltan datos críticos, pídelos antes de redactar.
""",
    )


def build_agente_conceptos_juridicos() -> Agent:
    return _build_agent(
        AGENTE_CONCEPTOS_JURIDICOS,
        """
Eres CONCEPTOS JURÍDICOS (REQ-029 a REQ-032).
Un concepto debe incluir: nombre del cliente, descripción del problema jurídico,
normas vigentes consultadas, conclusión y recomendación favorable. Usa leer_normas_clave
y leer_area_derecho para fundamentar; no inventes normas.
""",
    )


def build_agente_tutela_constitucional() -> Agent:
    return _build_agent(
        AGENTE_TUTELA_CONSTITUCIONAL,
        """
Eres TUTELA CONSTITUCIONAL (REQ-038 a REQ-040).
Redactas acciones de tutela con datos completos del accionante y accionado, el derecho
fundamental presuntamente vulnerado y los fundamentos de derecho. Recuerda que el plazo
de 10 días hábiles debe vigilarse.
""",
    )


def build_agente_seguimiento_procesal() -> Agent:
    return _build_agent(
        AGENTE_SEGUIMIENTO_PROCESAL,
        """
Eres SEGUIMIENTO PROCESAL (REQ-043 a REQ-047).
Estructuras el seguimiento de procesos, radicaciones y estados a partir de los datos que
el abogado aporta, y rediges informes mensuales de novedades para el cliente.
""",
    )


_SPECIALIST_BUILDERS = (
    build_agente_conocimiento_derecho,
    build_agente_recepcionista,
    build_agente_estrategia_casos,
    build_agente_servicio_cliente,
    build_agente_coordinador_civil,
    build_agente_coordinador_penal,
    build_agente_redaccion_documental,
    build_agente_conceptos_juridicos,
    build_agente_tutela_constitucional,
    build_agente_seguimiento_procesal,
)


def build_orchestrator() -> Agent:
    """Construye el coordinador principal de la firma."""
    base = load_system_prompt()
    specialists = [builder() for builder in _SPECIALIST_BUILDERS]
    handoffs = [handoff(agent) for agent in specialists]
    instructions = f"""{base}

Eres el COORDINADOR PRINCIPAL de la firma. Enrutas cada consulta al especialista adecuado:
- Áreas del derecho y cobertura -> {AGENTE_CONOCIMIENTO_DERECHO}
- Orden de hechos y apertura del caso -> {AGENTE_RECEPCIONISTA}
- Riesgos, teoría del caso, estrategia, pruebas, entrevistas -> {AGENTE_ESTRATEGIA_CASOS}
- Atención al cliente, explicaciones sencillas, correos -> {AGENTE_SERVICIO_CLIENTE}
- Proceso civil (CGP) -> {AGENTE_COORDINADOR_CIVIL}
- Proceso penal (Ley 906), representación de víctimas -> {AGENTE_COORDINADOR_PENAL}
- Contratos, recursos, solicitudes, excepciones, memoriales -> {AGENTE_REDACTION_DOCUMENTAL}
- Conceptos jurídicos -> {AGENTE_CONCEPTOS_JURIDICOS}
- Acciones de tutela -> {AGENTE_TUTELA_CONSTITUCIONAL}
- Seguimiento de procesos, radicaciones, informes mensuales -> {AGENTE_SEGUIMIENTO_PROCESAL}

Todas las capacidades están activas. Si faltan datos para analizar o redactar,
pídelos de forma concreta y mantén la conversación abierta. No inventes normas,
sentencias ni radicados.
"""
    return Agent(
        name=AGENTE_COORDINADOR_PRINCIPAL,
        instructions=instructions,
        model=get_settings().openai_model,
        handoffs=handoffs,
        tools=get_knowledge_tools(),
    )
