"""Definición de agentes por fase — OpenAI Agents SDK."""

from agents import Agent, handoff

from src.config import get_settings
from src.mcp.tools import get_knowledge_tools


def _load_prompt(name: str) -> str:
    settings = get_settings()
    path = settings.agente_dir / "prompts" / name
    return path.read_text(encoding="utf-8")


def _base_prompt_name(active_phase: int) -> str:
    if active_phase >= 1:
        return "sistema-fase-1.md"
    return "sistema-fase-0.md"


def build_perfil_agent(active_phase: int) -> Agent:
    base = _load_prompt(_base_prompt_name(active_phase))
    instructions = f"""{base}

Eres el especialista en PERFIL del despacho (REQ-001 a REQ-003).
Responde sobre identidad, experiencia, tono y forma de trabajo del asistente jurídico.
Si preguntan por áreas específicas del derecho, deriva al especialista en conocimiento.
"""
    return Agent(
        name="perfil_abogado_colombia",
        instructions=instructions,
        model=get_settings().openai_model,
    )


def build_conocimiento_agent(active_phase: int) -> Agent:
    base = _load_prompt(_base_prompt_name(active_phase))
    instructions = f"""{base}

Eres el especialista en CONOCIMIENTO por áreas (REQ-004 a REQ-011).
Usa las herramientas listar_areas_derecho y leer_area_derecho para responder.
Solo cita contenido presente en la base; si falta información, dilo claramente.
"""
    return Agent(
        name="conocimiento_areas_derecho",
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_knowledge_tools(),
    )


def build_comunicacion_agent(active_phase: int) -> Agent:
    base = _load_prompt(_base_prompt_name(active_phase))
    instructions = f"""{base}

Eres especialista en COMUNICACIÓN Y ATENCIÓN A CLIENTES (KAN-11, REQ-012 a REQ-015).
Objetivo:
- Responder con empatía y claridad profesional.
- Explicar escenarios jurídicos en lenguaje sencillo sin perder precisión.
- Redactar borradores de correos corporativos o mensajes profesionales.

Siempre mantén tono prudente y accionable. No emitas decisiones definitivas:
propón opciones para revisión del abogado.
"""
    return Agent(
        name="comunicacion_clientes_fase1",
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_knowledge_tools(),
    )


def build_analisis_agent(active_phase: int) -> Agent:
    base = _load_prompt(_base_prompt_name(active_phase))
    instructions = f"""{base}

Eres especialista en ANÁLISIS DE CONSULTAS, RIESGOS Y ESTRATEGIA (KAN-12, REQ-016 a REQ-021).
Objetivo:
- Identificar riesgos jurídicos.
- Ordenar hechos y construir narrativa útil para el caso.
- Diferenciar asuntos civiles y penales.
- Proponer teoría preliminar del caso, pruebas faltantes y debilidades del escrito rival.

Formula conclusiones preliminares, no definitivas. Expón supuestos y datos faltantes.
"""
    return Agent(
        name="analisis_riesgo_fase1",
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_knowledge_tools(),
    )


def build_redaccion_agent(active_phase: int) -> Agent:
    base = _load_prompt(_base_prompt_name(active_phase))
    instructions = f"""{base}

Eres especialista en REDACCIÓN BÁSICA (KAN-13, REQ-024 a REQ-028).
Objetivo:
- Redactar borradores de contratos y escritos básicos.
- Proponer estructura, cláusulas sugeridas y advertencias de riesgo contractual.
- Redactar recursos, solicitudes y excepciones en formato profesional.

No asumas hechos no aportados por el usuario. Si faltan datos críticos, pide la información.
"""
    return Agent(
        name="redaccion_basica_fase1",
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_knowledge_tools(),
    )


def build_orchestrator() -> Agent:
    settings = get_settings()
    active_phase = settings.active_phase
    base = _load_prompt(_base_prompt_name(active_phase))
    perfil = build_perfil_agent(active_phase)
    conocimiento = build_conocimiento_agent(active_phase)

    handoffs = [handoff(perfil), handoff(conocimiento)]
    name = "orquestador_fase0"
    instructions = f"""{base}

Eres el ORQUESTADOR Fase 0 (KAN-5).
Enruta consultas de perfil y áreas del derecho a los especialistas correspondientes.
Si piden redacción de documentos, análisis de riesgos o estrategia procesal, informa
que la capacidad pertenece a una fase posterior y no está activa.
"""

    if active_phase >= 1:
        comunicacion = build_comunicacion_agent(active_phase)
        analisis = build_analisis_agent(active_phase)
        redaccion = build_redaccion_agent(active_phase)
        handoffs.extend([handoff(comunicacion), handoff(analisis), handoff(redaccion)])
        name = "orquestador_fase1"
        instructions = f"""{base}

Eres el ORQUESTADOR Fase 1 (KAN-6). Enrutas consultas así:
- Perfil/identidad/experiencia del asistente -> perfil_abogado_colombia
- Áreas del derecho y cobertura -> conocimiento_areas_derecho
- Atención al cliente, explicaciones sencillas, correos profesionales -> comunicacion_clientes_fase1
- Riesgos, estrategia, teoría del caso, debilidades y pruebas faltantes -> analisis_riesgo_fase1
- Redacción básica de contratos/escritos/recursos/solicitudes/excepciones -> redaccion_basica_fase1

No habilites capacidades de Fase 2 o Fase 3 (seguimiento procesal avanzado, memoriales,
tutelas o conceptos jurídicos especializados). Si faltan datos para redactar o analizar,
pide información adicional de manera concreta.
"""

    return Agent(
        name=name,
        instructions=instructions,
        model=settings.openai_model,
        handoffs=handoffs,
        tools=get_knowledge_tools(),
    )
