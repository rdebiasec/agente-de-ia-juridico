"""Subsistema penal — representación de víctimas (Ley 906)."""

from agents import Agent, handoff

from src.agents.agent_names import (
    AGENTE_COORDINADOR_PENAL,
    SUBAGENTE_INVESTIGACION_VICTIMA,
    SUBAGENTE_PENAL_GARANTIAS,
    SUBAGENTE_PENAL_JUICIOS,
    SUBAGENTE_PENAL_NEGOCIACION,
    SUBAGENTE_PENAL_PRUEBAS,
    SUBAGENTE_PENAL_REPARACION,
    SUBAGENTE_PENAL_RECURSOS,
)
from src.agents.system_prompt import load_system_prompt
from src.config import get_settings
from src.mcp.penal_tools import get_penal_victima_tools

_POSTURA_VICTIMA = """
POSTURA DEL DESPACHO (innegociable): representas exclusivamente a la VÍCTIMA.
Nunca asumas defensa del imputado ni prepares argumentos de descargo.
Si falta radicado, etapa o identidad de partes, pídelos antes de concluir.
"""


def _build_penal_agent(name: str, rol_instructions: str) -> Agent:
    base = load_system_prompt()
    instructions = f"{base}\n\n{_POSTURA_VICTIMA}\n\n{rol_instructions.strip()}\n"
    return Agent(
        name=name,
        instructions=instructions,
        model=get_settings().openai_model,
        tools=get_penal_victima_tools(name),
    )


def build_subagente_investigacion_victima() -> Agent:
    return _build_penal_agent(
        SUBAGENTE_INVESTIGACION_VICTIMA,
        """
Eres el subagente de INVESTIGACIÓN VÍCTIMA ante la Fiscalía (REQ-007, REQ-017, REQ-020, REQ-023).
Usa leer_kb_penal_victima('derechos'), preparar_denuncia_victima y preparar_peticion_fiscal.
""",
    )


def build_subagente_penal_garantias() -> Agent:
    return _build_penal_agent(
        SUBAGENTE_PENAL_GARANTIAS,
        """
Eres el subagente PENAL GARANTÍAS (REQ-007, REQ-023, REQ-037).
Usa leer_kb_penal_victima('garantias'), preparar_audiencia_garantias y evaluar_medidas_proteccion_victima.
""",
    )


def build_subagente_penal_juicios() -> Agent:
    return _build_penal_agent(
        SUBAGENTE_PENAL_JUICIOS,
        """
Eres el subagente PENAL JUICIOS — acusación, preparatoria y juicio oral (REQ-007, REQ-023, REQ-027, REQ-037).
Usa leer_kb_penal_victima('conocimiento'), preparar_audiencia_preparatoria, preparar_juicio_oral,
preparar_interrogatorio_victima y preparar_alegatos_victima.
""",
    )


def build_subagente_penal_pruebas() -> Agent:
    return _build_penal_agent(
        SUBAGENTE_PENAL_PRUEBAS,
        """
Eres el subagente PENAL PRUEBAS (REQ-020 a REQ-023).
Usa leer_kb_penal_victima('prueba'), construir_teoria_probatoria_victima, generar_matriz_prueba y
evaluar_objecion_prueba.
""",
    )


def build_subagente_penal_reparacion() -> Agent:
    return _build_penal_agent(
        SUBAGENTE_PENAL_REPARACION,
        """
Eres el subagente PENAL REPARACIÓN INTEGRAL (REQ-007, REQ-019, REQ-027).
Usa leer_kb_penal_victima('reparacion'), estimar_rubros_reparacion, preparar_memorial_reparacion.
NO inventes cifras.
""",
    )


def build_subagente_penal_negociacion() -> Agent:
    return _build_penal_agent(
        SUBAGENTE_PENAL_NEGOCIACION,
        """
Eres el subagente PENAL NEGOCIACIÓN — salidas alternas (REQ-007, REQ-016, REQ-019).
Usa leer_kb_penal_victima('negociacion'), evaluar_preacuerdo_victima y evaluar_oposicion_principio_oportunidad.
""",
    )


def build_subagente_penal_recursos() -> Agent:
    return _build_penal_agent(
        SUBAGENTE_PENAL_RECURSOS,
        """
Eres el subagente PENAL RECURSOS (REQ-028, REQ-027).
Usa leer_kb_penal_victima('recursos'), evaluar_recurso_penal y preparar_recurso_penal.
""",
    )


_PENAL_SPECIALIST_BUILDERS = (
    build_subagente_investigacion_victima,
    build_subagente_penal_garantias,
    build_subagente_penal_juicios,
    build_subagente_penal_pruebas,
    build_subagente_penal_reparacion,
    build_subagente_penal_negociacion,
    build_subagente_penal_recursos,
)


def build_agente_coordinador_penal() -> Agent:
    base = load_system_prompt()
    specialists = [builder() for builder in _PENAL_SPECIALIST_BUILDERS]
    handoffs = [handoff(agent) for agent in specialists]
    instructions = f"""{base}

{_POSTURA_VICTIMA}

Eres el COORDINADOR PENAL. Diriges el subsistema penal para víctimas (Ley 906).
Enrutas según etapa y objeto:

- Denuncia, querella, Fiscalía, indagación, carpeta -> {SUBAGENTE_INVESTIGACION_VICTIMA}
- Captura, legalización, imputación, aseguramiento, garantías -> {SUBAGENTE_PENAL_GARANTIAS}
- Acusación, preparatoria, juicio oral, alegatos, interrogatorio -> {SUBAGENTE_PENAL_JUICIOS}
- Prueba, testigo, perito, objeción, cadena de custodia -> {SUBAGENTE_PENAL_PRUEBAS}
- Reparación, indemnización, perjuicios -> {SUBAGENTE_PENAL_REPARACION}
- Preacuerdo, principio de oportunidad, negociación -> {SUBAGENTE_PENAL_NEGOCIACION}
- Recurso, apelación, casación, reposición -> {SUBAGENTE_PENAL_RECURSOS}

Usa detectar_etapa_penal y clasificar_objeto_penal cuando la consulta sea ambigua.
No inventes normas, sentencias ni radicados.
"""
    return Agent(
        name=AGENTE_COORDINADOR_PENAL,
        instructions=instructions,
        model=get_settings().openai_model,
        handoffs=handoffs,
        tools=get_penal_victima_tools(AGENTE_COORDINADOR_PENAL),
    )


build_coordinador_penal = build_agente_coordinador_penal
build_litigante_orquestador_penal = build_agente_coordinador_penal
