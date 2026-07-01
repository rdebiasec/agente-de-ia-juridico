"""Subsistema civil — CGP (Ley 1564 de 2012)."""

from agents import Agent, handoff

from src.agents.agent_names import (
    AGENTE_CIVIL_AUDIENCIA_INICIAL,
    AGENTE_CIVIL_CONTESTACION,
    AGENTE_CIVIL_DEMANDA,
    AGENTE_CIVIL_EJECUCION,
    AGENTE_CIVIL_INSTRUCCION,
    AGENTE_CIVIL_PRUEBA,
    AGENTE_CIVIL_RECURSOS,
    AGENTE_COORDINADOR_CIVIL,
)
from src.agents.system_prompt import load_system_prompt
from src.config import get_settings
from src.mcp.civil_tools import get_civil_tools

_POSTURA_CIVIL = """
En civil identifica siempre el rol del despacho (demandante o demandado) antes de redactar.
Si faltan radicado, etapa o partes, pídelos antes de concluir.
"""


def _build_civil_agent(name: str, rol_instructions: str) -> Agent:
    base = load_system_prompt()
    instructions = f"{base}\n\n{_POSTURA_CIVIL}\n\n{rol_instructions.strip()}\n"
    return Agent(
        name=name,
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_civil_tools(name),
    )


def build_agente_civil_demanda() -> Agent:
    return _build_civil_agent(
        AGENTE_CIVIL_DEMANDA,
        """
Eres el agente CIVIL DEMANDA (REQ-024, REQ-027).
Etapa: conciliación previa (si aplica), demanda, reparto, admisión y notificación.
Usa leer_kb_civil('demanda'), preparar_demanda_civil.
""",
    )


def build_agente_civil_contestacion() -> Agent:
    return _build_civil_agent(
        AGENTE_CIVIL_CONTESTACION,
        """
Eres el agente CIVIL CONTESTACIÓN (REQ-024, REQ-028).
Etapa: traslado, contestación, excepciones, reconvención.
Usa leer_kb_civil('contestacion'), preparar_contestacion_civil.
""",
    )


def build_agente_civil_audiencia_inicial() -> Agent:
    return _build_civil_agent(
        AGENTE_CIVIL_AUDIENCIA_INICIAL,
        """
Eres el agente CIVIL AUDIENCIA INICIAL art. 372 CGP (REQ-027, REQ-037).
Usa leer_kb_civil('audiencia_372'), preparar_audiencia_372.
""",
    )


def build_agente_civil_instruccion() -> Agent:
    return _build_civil_agent(
        AGENTE_CIVIL_INSTRUCCION,
        """
Eres el agente CIVIL INSTRUCCIÓN art. 373 CGP (REQ-027, REQ-037).
Usa leer_kb_civil('audiencia_373'), preparar_audiencia_373.
""",
    )


def build_agente_civil_prueba() -> Agent:
    return _build_civil_agent(
        AGENTE_CIVIL_PRUEBA,
        """
Eres el agente CIVIL PRUEBA (REQ-020 a REQ-023).
Usa leer_kb_civil('prueba'), generar_matriz_prueba_civil.
""",
    )


def build_agente_civil_recursos() -> Agent:
    return _build_civil_agent(
        AGENTE_CIVIL_RECURSOS,
        """
Eres el agente CIVIL RECURSOS (REQ-028, REQ-027).
Usa leer_kb_civil('recursos'), preparar_recurso_civil.
""",
    )


def build_agente_civil_ejecucion() -> Agent:
    return _build_civil_agent(
        AGENTE_CIVIL_EJECUCION,
        """
Eres el agente CIVIL EJECUCIÓN (REQ-027).
Usa leer_kb_civil('ejecucion'), preparar_ejecucion_civil.
""",
    )


_CIVIL_SPECIALIST_BUILDERS = (
    build_agente_civil_demanda,
    build_agente_civil_contestacion,
    build_agente_civil_audiencia_inicial,
    build_agente_civil_instruccion,
    build_agente_civil_prueba,
    build_agente_civil_recursos,
    build_agente_civil_ejecucion,
)


def build_agente_coordinador_civil() -> Agent:
    base = load_system_prompt()
    specialists = [builder() for builder in _CIVIL_SPECIALIST_BUILDERS]
    handoffs = [handoff(agent) for agent in specialists]
    instructions = f"""{base}

{_POSTURA_CIVIL}

Eres el COORDINADOR CIVIL. Diriges el subsistema civil bajo el CGP.
Enrutas según etapa y objeto:

- Demanda, admisión, conciliación, reparto -> {AGENTE_CIVIL_DEMANDA}
- Contestación, excepciones, reconvención, traslado -> {AGENTE_CIVIL_CONTESTACION}
- Audiencia inicial, art. 372 -> {AGENTE_CIVIL_AUDIENCIA_INICIAL}
- Instrucción, juzgamiento, art. 373 -> {AGENTE_CIVIL_INSTRUCCION}
- Prueba, testigo, perito, matriz -> {AGENTE_CIVIL_PRUEBA}
- Recurso, apelación, casación -> {AGENTE_CIVIL_RECURSOS}
- Ejecución, embargo, remate -> {AGENTE_CIVIL_EJECUCION}

Usa detectar_etapa_civil cuando la consulta sea ambigua.
No inventes normas, sentencias ni radicados.
"""
    return Agent(
        name=AGENTE_COORDINADOR_CIVIL,
        instructions=instructions,
        model=get_settings().openai_model,
        handoffs=handoffs,
        tools=get_civil_tools(AGENTE_COORDINADOR_CIVIL),
    )


build_coordinador_civil = build_agente_coordinador_civil
