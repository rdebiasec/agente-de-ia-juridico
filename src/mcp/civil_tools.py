"""Tools del subsistema civil — CGP (Ley 1564 de 2012)."""

from __future__ import annotations

import re

from agents import function_tool

from src.config import get_settings
from src.mcp.tools import (
    buscar_en_conocimiento,
    buscar_en_expediente,
    leer_area_derecho,
    leer_normas_clave,
    leer_playbook_proceso,
    listar_areas_derecho,
)

CIVIL_KB = {
    "playbook": "proceso-civil-cgp.md",
    "demanda": "civil-demanda-cgp.md",
    "contestacion": "civil-contestacion-cgp.md",
    "audiencia_372": "civil-audiencia-372-cgp.md",
    "audiencia_373": "civil-audiencia-373-cgp.md",
    "prueba": "civil-prueba-cgp.md",
    "recursos": "civil-recursos-cgp.md",
    "ejecucion": "civil-ejecucion-cgp.md",
}

_DEMANDA_RE = re.compile(
    r"\b(demanda|admisi[oó]n|reparto|conciliaci[oó]n|mandamiento de pago|procedibilidad)\b",
    re.IGNORECASE,
)
_CONTESTACION_RE = re.compile(
    r"\b(contestaci[oó]n|excepci[oó]n|reconvenci[oó]n|traslado)\b",
    re.IGNORECASE,
)
_AUDIENCIA_372_RE = re.compile(
    r"\b(audiencia inicial|art\.?\s*372|372|fijaci[oó]n del litigio)\b",
    re.IGNORECASE,
)
_INSTRUCCION_RE = re.compile(
    r"\b(audiencia de instrucci[oó]n|juzgamiento|art\.?\s*373|373|alegatos de conclusi[oó]n)\b",
    re.IGNORECASE,
)
_PRUEBA_RE = re.compile(
    r"\b(prueba|testigo|perito|objeci[oó]n|decreto de pruebas|matriz)\b",
    re.IGNORECASE,
)
_RECURSOS_RE = re.compile(
    r"\b(recurso|apelaci[oó]n|casaci[oó]n|reposici[oó]n|queja|s[uú]plica)\b",
    re.IGNORECASE,
)
_EJECUCION_RE = re.compile(
    r"\b(ejecuci[oó]n|t[ií]tulo ejecutivo|embargo|remate|liquidaci[oó]n de cr[eé]dito)\b",
    re.IGNORECASE,
)


def _read_civil_kb(name: str) -> str:
    settings = get_settings()
    path = settings.agente_dir / "conocimiento" / name
    if not path.exists():
        return f"[No encontrado: {name}]"
    return path.read_text(encoding="utf-8")


def infer_civil_specialist(mensaje: str) -> str:
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

    if _EJECUCION_RE.search(mensaje):
        return AGENTE_CIVIL_EJECUCION
    if _RECURSOS_RE.search(mensaje):
        return AGENTE_CIVIL_RECURSOS
    if _INSTRUCCION_RE.search(mensaje):
        return AGENTE_CIVIL_INSTRUCCION
    if _AUDIENCIA_372_RE.search(mensaje):
        return AGENTE_CIVIL_AUDIENCIA_INICIAL
    if _CONTESTACION_RE.search(mensaje):
        return AGENTE_CIVIL_CONTESTACION
    if _PRUEBA_RE.search(mensaje) and not _DEMANDA_RE.search(mensaje):
        return AGENTE_CIVIL_PRUEBA
    if _DEMANDA_RE.search(mensaje):
        return AGENTE_CIVIL_DEMANDA
    return AGENTE_COORDINADOR_CIVIL


def infer_etapa_civil(mensaje: str, etapa_expediente: str = "") -> str:
    texto = f"{mensaje} {etapa_expediente}".lower()
    if _EJECUCION_RE.search(texto):
        return "ejecucion"
    if _RECURSOS_RE.search(texto):
        return "recursos"
    if _INSTRUCCION_RE.search(texto):
        return "instruccion_juzgamiento"
    if _AUDIENCIA_372_RE.search(texto):
        return "audiencia_inicial"
    if _CONTESTACION_RE.search(texto):
        return "contestacion"
    if _DEMANDA_RE.search(texto):
        return "demanda_admision"
    if etapa_expediente.strip():
        return etapa_expediente.strip().lower()
    return "indeterminada"


@function_tool
def leer_kb_civil(tema: str) -> str:
    """Lee KB civil: playbook, demanda, contestacion, audiencia_372, audiencia_373, prueba, recursos, ejecucion."""
    key = tema.strip().lower().replace(" ", "_")
    filename = CIVIL_KB.get(key)
    if not filename:
        opciones = ", ".join(sorted(CIVIL_KB))
        return f"Tema no reconocido: {tema}. Opciones: {opciones}."
    return _read_civil_kb(filename)


@function_tool
def detectar_etapa_civil(mensaje: str, etapa_expediente: str = "") -> str:
    """Clasifica etapa civil CGP: demanda, contestacion, audiencia_inicial, instruccion, recursos, ejecucion."""
    etapa = infer_etapa_civil(mensaje, etapa_expediente)
    return f"Etapa civil detectada: {etapa}. Confirmar con el abogado si hay actuación reciente."


@function_tool
def preparar_demanda_civil(hechos: str, pretensiones: str, rol_despacho: str = "demandante") -> str:
    """Estructura borrador de demanda o actuación de demandante."""
    return (
        f"BORRADOR — Demanda / actuación demandante (rol: {rol_despacho.strip()})\n"
        f"Hechos:\n{hechos.strip()}\n"
        f"Pretensiones:\n{pretensiones.strip()}\n"
        "Verificar conciliación previa, competencia, cuantía y anexos.\n"
        "Consultar leer_kb_civil('demanda')."
    )


@function_tool
def preparar_contestacion_civil(hechos: str, excepciones: str, rol_despacho: str = "demandado") -> str:
    """Estructura contestación, excepciones y reconvención."""
    return (
        f"BORRADOR — Contestación (rol: {rol_despacho.strip()})\n"
        f"Hechos:\n{hechos.strip()}\n"
        f"Excepciones propuestas:\n{excepciones.strip() or '(evaluar)'}\n"
        "Consultar leer_kb_civil('contestacion')."
    )


@function_tool
def preparar_audiencia_372(objeto: str, pruebas: str) -> str:
    """Plan audiencia inicial art. 372 CGP."""
    return (
        "PLAN — Audiencia inicial (art. 372)\n"
        f"Objeto: {objeto.strip()}\n"
        f"Pruebas a proponer:\n{pruebas.strip()}\n"
        "Incluir: conciliación, interrogatorio partes, fijación litigio, excepciones previas."
    )


@function_tool
def preparar_audiencia_373(pruebas: str, teoria_caso: str) -> str:
    """Plan audiencia instrucción y juzgamiento art. 373 CGP."""
    return (
        "PLAN — Instrucción y juzgamiento (art. 373)\n"
        f"Teoría del caso:\n{teoria_caso.strip()}\n"
        f"Pruebas:\n{pruebas.strip()}\n"
        "Incluir orden de práctica, interrogatorios y alegatos de conclusión."
    )


@function_tool
def generar_matriz_prueba_civil(hechos_a_probar: str) -> str:
    """Plantilla matriz de prueba civil."""
    hechos = [h.strip() for h in hechos_a_probar.split(";") if h.strip()]
    if not hechos:
        hechos = [hechos_a_probar.strip()] if hechos_a_probar.strip() else ["(indicar hecho)"]
    lineas = ["MATRIZ DE PRUEBA CIVIL", "| Hecho | Medio | Fuente | Estado |", "|---|---|---|---|"]
    for hecho in hechos:
        lineas.append(f"| {hecho} | (definir) | (definir) | pendiente |")
    return "\n".join(lineas)


@function_tool
def preparar_recurso_civil(tipo: str, argumentos: str) -> str:
    """Estructura memorial de recurso civil."""
    return (
        f"BORRADOR — Recurso civil ({tipo.strip()})\n"
        f"Argumentos:\n{argumentos.strip()}\n"
        "Incluir: destinatario, radicado, decisión impugnada, petición."
    )


@function_tool
def preparar_ejecucion_civil(titulo: str, pretension: str) -> str:
    """Estructura actuación de ejecución de sentencia o título."""
    return (
        "BORRADOR — Ejecución civil\n"
        f"Título/base: {titulo.strip()}\n"
        f"Petición:\n{pretension.strip()}\n"
        "Consultar leer_kb_civil('ejecucion')."
    )


_COORDINATOR_TOOLS = [
    detectar_etapa_civil,
    leer_kb_civil,
    leer_playbook_proceso,
    listar_areas_derecho,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_DEMANDA_TOOLS = [
    leer_kb_civil,
    leer_playbook_proceso,
    leer_area_derecho,
    preparar_demanda_civil,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_CONTESTACION_TOOLS = [
    leer_kb_civil,
    leer_playbook_proceso,
    preparar_contestacion_civil,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_AUDIENCIA_372_TOOLS = [
    leer_kb_civil,
    preparar_audiencia_372,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_INSTRUCCION_TOOLS = [
    leer_kb_civil,
    preparar_audiencia_373,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_PRUEBA_TOOLS = [
    leer_kb_civil,
    generar_matriz_prueba_civil,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_RECURSOS_TOOLS = [
    leer_kb_civil,
    leer_normas_clave,
    preparar_recurso_civil,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_EJECUCION_TOOLS = [
    leer_kb_civil,
    preparar_ejecucion_civil,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

from src.agents.agent_names import (  # noqa: E402
    AGENTE_CIVIL_AUDIENCIA_INICIAL,
    AGENTE_CIVIL_CONTESTACION,
    AGENTE_CIVIL_DEMANDA,
    AGENTE_CIVIL_EJECUCION,
    AGENTE_CIVIL_INSTRUCCION,
    AGENTE_CIVIL_PRUEBA,
    AGENTE_CIVIL_RECURSOS,
    AGENTE_COORDINADOR_CIVIL,
)

_CIVIL_AGENT_TOOLS: dict[str, list] = {
    AGENTE_COORDINADOR_CIVIL: _COORDINATOR_TOOLS,
    AGENTE_CIVIL_DEMANDA: _DEMANDA_TOOLS,
    AGENTE_CIVIL_CONTESTACION: _CONTESTACION_TOOLS,
    AGENTE_CIVIL_AUDIENCIA_INICIAL: _AUDIENCIA_372_TOOLS,
    AGENTE_CIVIL_INSTRUCCION: _INSTRUCCION_TOOLS,
    AGENTE_CIVIL_PRUEBA: _PRUEBA_TOOLS,
    AGENTE_CIVIL_RECURSOS: _RECURSOS_TOOLS,
    AGENTE_CIVIL_EJECUCION: _EJECUCION_TOOLS,
}


def get_civil_tools(agent_name: str) -> list:
    return list(_CIVIL_AGENT_TOOLS.get(agent_name, _COORDINATOR_TOOLS))
