"""Tools del subsistema penal — representación de víctimas (Ley 906)."""

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

PENAL_VICTIMA_KB = {
    "playbook": "proceso-penal-victima-906.md",
    "derechos": "derechos-victima-ley906.md",
    "garantias": "audiencias-garantias-victima.md",
    "conocimiento": "intervencion-victima-conocimiento.md",
    "prueba": "prueba-penal-victima.md",
    "reparacion": "reparacion-integral-victima.md",
    "negociacion": "salidas-alternas-victima.md",
    "recursos": "recursos-penales-victima.md",
}

_INVESTIGACION_RE = re.compile(
    r"\b(denuncia|querella|fiscal[ií]a|indagaci[oó]n|carpeta|noticia criminal)\b",
    re.IGNORECASE,
)
_GARANTIAS_RE = re.compile(
    r"\b(captura|legalizaci[oó]n|imputaci[oó]n|aseguramiento|garant[ií]as|preliminar)\b",
    re.IGNORECASE,
)
_CONOCIMIENTO_RE = re.compile(
    r"\b(acusaci[oó]n|preparatoria|juicio oral|alegato|interrogatorio)\b",
    re.IGNORECASE,
)
_PRUEBA_RE = re.compile(
    r"\b(prueba|testigo|perito|objeci[oó]n|cadena de custodia|pericial)\b",
    re.IGNORECASE,
)
_REPARACION_RE = re.compile(
    r"\b(reparaci[oó]n|indemnizaci[oó]n|perjuicio|lucro cesante|da[nñ]o emergente|moral)\b",
    re.IGNORECASE,
)
_NEGOCIACION_RE = re.compile(
    r"\b(preacuerdo|principio de oportunidad|negociaci[oó]n|salida alterna)\b",
    re.IGNORECASE,
)
_RECURSOS_RE = re.compile(
    r"\b(recurso|apelaci[oó]n|casaci[oó]n|reposici[oó]n|impugnar)\b",
    re.IGNORECASE,
)

_OBJETO_AUDIENCIA_RE = re.compile(r"\b(audiencia|interrogatorio|alegato)\b", re.IGNORECASE)
_OBJETO_MEMORIAL_RE = re.compile(r"\b(memorial|escrito|petici[oó]n|denuncia|querella)\b", re.IGNORECASE)
_OBJETO_PRUEBA_RE = re.compile(r"\b(prueba|matriz|testigo|perito)\b", re.IGNORECASE)
_OBJETO_REPARACION_RE = re.compile(r"\b(reparaci[oó]n|indemnizaci[oó]n|rubro)\b", re.IGNORECASE)
_OBJETO_NEGOCIACION_RE = re.compile(r"\b(preacuerdo|negociaci[oó]n|oportunidad)\b", re.IGNORECASE)
_OBJETO_RECURSO_RE = re.compile(r"\b(recurso|apelaci[oó]n|casaci[oó]n)\b", re.IGNORECASE)


def _read_penal_kb(name: str) -> str:
    settings = get_settings()
    path = settings.agente_dir / "conocimiento" / name
    if not path.exists():
        return f"[No encontrado: {name}]"
    return path.read_text(encoding="utf-8")


def _infer_etapa(mensaje: str, etapa_expediente: str = "") -> str:
    texto = f"{mensaje} {etapa_expediente}".lower()
    if _RECURSOS_RE.search(texto):
        return "recursos"
    if _CONOCIMIENTO_RE.search(texto):
        return "conocimiento"
    if _GARANTIAS_RE.search(texto):
        return "garantias"
    if _INVESTIGACION_RE.search(texto):
        return "indagacion"
    if etapa_expediente.strip():
        return etapa_expediente.strip().lower()
    return "indeterminada"


def _infer_objeto(mensaje: str) -> str:
    texto = mensaje.lower()
    if _OBJETO_RECURSO_RE.search(texto):
        return "recurso"
    if _OBJETO_NEGOCIACION_RE.search(texto):
        return "negociacion"
    if _OBJETO_REPARACION_RE.search(texto):
        return "reparacion"
    if _OBJETO_PRUEBA_RE.search(texto):
        return "prueba"
    if _OBJETO_MEMORIAL_RE.search(texto):
        return "memorial"
    if _OBJETO_AUDIENCIA_RE.search(texto):
        return "audiencia"
    return "consulta_general"


def infer_penal_specialist(mensaje: str) -> str:
    """Infiere el subagente penal especialista (para fallback y trazas)."""
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

    if _RECURSOS_RE.search(mensaje):
        return SUBAGENTE_PENAL_RECURSOS
    if _NEGOCIACION_RE.search(mensaje):
        return SUBAGENTE_PENAL_NEGOCIACION
    if _REPARACION_RE.search(mensaje):
        return SUBAGENTE_PENAL_REPARACION
    if _PRUEBA_RE.search(mensaje):
        return SUBAGENTE_PENAL_PRUEBAS
    if _CONOCIMIENTO_RE.search(mensaje):
        return SUBAGENTE_PENAL_JUICIOS
    if _GARANTIAS_RE.search(mensaje):
        return SUBAGENTE_PENAL_GARANTIAS
    if _INVESTIGACION_RE.search(mensaje):
        return SUBAGENTE_INVESTIGACION_VICTIMA
    return AGENTE_COORDINADOR_PENAL


@function_tool
def leer_playbook_penal_victima() -> str:
    """Lee el playbook integral de representación de víctimas (Ley 906)."""
    return _read_penal_kb(PENAL_VICTIMA_KB["playbook"])


@function_tool
def leer_kb_penal_victima(tema: str) -> str:
    """Lee KB penal víctima: derechos, garantias, conocimiento, prueba, reparacion, negociacion, recursos."""
    key = tema.strip().lower().replace(" ", "_")
    filename = PENAL_VICTIMA_KB.get(key)
    if not filename:
        opciones = ", ".join(sorted(PENAL_VICTIMA_KB))
        return f"Tema no reconocido: {tema}. Opciones: {opciones}, playbook."
    return _read_penal_kb(filename)


def infer_etapa_penal(mensaje: str, etapa_expediente: str = "") -> str:
    """Clasifica etapa penal (función pura, usable en tests y tools)."""
    return _infer_etapa(mensaje, etapa_expediente)


@function_tool
def detectar_etapa_penal(mensaje: str, etapa_expediente: str = "") -> str:
    """Clasifica la etapa penal: indagacion, garantias, conocimiento, recursos o indeterminada."""
    etapa = infer_etapa_penal(mensaje, etapa_expediente)
    return (
        f"Etapa detectada: {etapa}. "
        "Confirme con el abogado si hay radicado o actuación reciente que modifique la etapa."
    )


@function_tool
def clasificar_objeto_penal(mensaje: str) -> str:
    """Clasifica el objeto: audiencia, memorial, prueba, reparacion, negociacion, recurso o consulta_general."""
    objeto = _infer_objeto(mensaje)
    return f"Objeto litigioso detectado: {objeto}."


@function_tool
def preparar_denuncia_victima(hechos: str, partes: str, delito_presunto: str) -> str:
    """Estructura borrador de denuncia/querella (víctima). Campos: hechos, partes, delito presunto."""
    return (
        "BORRADOR ESTRUCTURAL — Denuncia/querella (víctima)\n"
        f"Delito presunto: {delito_presunto.strip()}\n"
        f"Partes: {partes.strip()}\n"
        "Hechos (orden cronológico):\n"
        f"{hechos.strip()}\n"
        "Pendiente: pretensiones (investigación, medidas de protección, reparación futura), "
        "anexos y lugar de radicación ante Fiscalía.\n"
        "Validar con schema DenunciaVictima antes de radicar."
    )


@function_tool
def preparar_peticion_fiscal(tipo: str, hechos: str) -> str:
    """Prepara estructura de petición al fiscal: medidas_proteccion, diligencias, acceso_carpeta, otra."""
    return (
        f"BORRADOR ESTRUCTURAL — Petición al fiscal ({tipo.strip()})\n"
        f"Hechos relevantes:\n{hechos.strip()}\n"
        "Incluir: fundamento, petición concreta, radicado/noticia criminal si existe.\n"
        "Consultar leer_kb_penal_victima('derechos') para fundamentar."
    )


@function_tool
def detectar_pruebas_faltantes_victima(hechos: str, pruebas_disponibles: str) -> str:
    """Lista pruebas potencialmente faltantes según hechos narrados y pruebas ya disponibles."""
    return (
        "CHECKLIST — Pruebas faltantes (víctima)\n"
        f"Hechos: {hechos.strip()}\n"
        f"Disponibles: {pruebas_disponibles.strip() or '(ninguna indicada)'}\n"
        "Revisar: testimonios presenciales, documentales (médicos, denuncias), peritajes, "
        "cadena de custodia, soporte de perjuicios para reparación.\n"
        "Usar generar_matriz_prueba para detalle por hecho."
    )


@function_tool
def preparar_audiencia_garantias(tipo: str, etapa: str) -> str:
    """Checklist para audiencia ante juez de garantías (legalización, imputación, aseguramiento, etc.)."""
    kb = _read_penal_kb(PENAL_VICTIMA_KB["garantias"])
    return (
        f"PLAN — Audiencia de garantías\nTipo: {tipo.strip()} | Etapa: {etapa.strip()}\n\n"
        f"{kb[:1200]}\n\n"
        "(Fragmento KB — usar leer_kb_penal_victima('garantias') para texto completo.)"
    )


@function_tool
def evaluar_medidas_proteccion_victima(hechos: str) -> str:
    """Evalúa si conviene solicitar medidas de protección según hechos (checklist, no decisión)."""
    return (
        "CHECKLIST — Medidas de protección (víctima)\n"
        f"Hechos: {hechos.strip()}\n"
        "Evaluar: amenazas, proximidad del imputado, menores involucrados, reincidencia, "
        "necesidad de protección de testigos.\n"
        "Petición sugerida: preparar_peticion_fiscal('medidas_proteccion', ...)."
    )


@function_tool
def preparar_audiencia_preparatoria(pruebas: str) -> str:
    """Plan para audiencia preparatoria: pruebas a enunciar y objeciones desde víctima."""
    return (
        "PLAN — Audiencia preparatoria (víctima)\n"
        f"Pruebas propuestas:\n{pruebas.strip()}\n"
        "Tareas: enunciar pruebas, formular objeciones, alinear con matriz de prueba y reparación."
    )


@function_tool
def preparar_juicio_oral(teoria_caso: str, pruebas: str) -> str:
    """Plan para juicio oral: teoría del caso y pruebas desde representación de víctima."""
    return (
        "PLAN — Juicio oral (víctima)\n"
        f"Teoría del caso:\n{teoria_caso.strip()}\n"
        f"Pruebas:\n{pruebas.strip()}\n"
        "Incluir: orden de práctica, interrogatorios, alegatos y pretensiones de reparación."
    )


@function_tool
def preparar_interrogatorio_victima(testigo: str, objetivo: str) -> str:
    """Estructura interrogatorio desde víctima: testigo y objetivo probatorio."""
    return (
        "BORRADOR — Interrogatorio (víctima)\n"
        f"Testigo: {testigo.strip()}\n"
        f"Objetivo probatorio: {objetivo.strip()}\n"
        "Bloques sugeridos: identificación, relación con hechos, desarrollo cronológico, "
        "detalles sensoriales, cierre.\n"
        "Validar con schema InterrogatorioVictima."
    )


@function_tool
def preparar_alegatos_victima(pretensiones: str) -> str:
    """Estructura de alegatos de cierre desde interés de la víctima."""
    return (
        "BORRADOR — Alegatos de cierre (víctima)\n"
        f"Pretensiones:\n{pretensiones.strip()}\n"
        "Estructura: hechos probados, responsabilidad, daño, pretensión de condena y reparación integral."
    )


@function_tool
def construir_teoria_probatoria_victima(hechos: str, cargos: str) -> str:
    """Esquema de teoría del caso probatorio para la víctima."""
    return (
        "TEORÍA PROBATORIA (víctima)\n"
        f"Hechos: {hechos.strip()}\n"
        f"Cargos/imputación: {cargos.strip()}\n"
        "Ejes: materialidad, autoría/participación, nexo causal, perjuicios."
    )


@function_tool
def generar_matriz_prueba(hechos_a_probar: str) -> str:
    """Genera plantilla de matriz de prueba (una fila por hecho listado)."""
    hechos = [h.strip() for h in hechos_a_probar.split(";") if h.strip()]
    if not hechos:
        hechos = [hechos_a_probar.strip()] if hechos_a_probar.strip() else ["(indicar hecho)"]
    lineas = ["MATRIZ DE PRUEBA — plantilla", "| Hecho | Medio | Fuente | Estado |", "|---|---|---|---|"]
    for hecho in hechos:
        lineas.append(f"| {hecho} | (definir) | (definir) | pendiente |")
    lineas.append("Completar con schema MatrizPrueba.")
    return "\n".join(lineas)


@function_tool
def evaluar_objecion_prueba(medio: str, fundamento: str) -> str:
    """Orientación para objeción de prueba (irrelevancia, ilegalidad, etc.)."""
    kb = _read_penal_kb(PENAL_VICTIMA_KB["prueba"])
    return (
        f"OBJECIÓN — Medio: {medio.strip()}\nFundamento: {fundamento.strip()}\n"
        f"Referencia KB (extracto):\n{kb[:800]}"
    )


@function_tool
def estimar_rubros_reparacion(hechos: str) -> str:
    """Lista rubros de reparación posibles sin inventar cifras."""
    return (
        "RUBROS — Reparación integral (sin cuantificación automática)\n"
        f"Hechos: {hechos.strip()}\n"
        "Rubros a evaluar: daño emergente, lucro cesante, daño moral, otros según delito.\n"
        "Para cada rubro indicar prueba necesaria (facturas, perito, testimonio).\n"
        "NO asignar montos sin soporte del abogado."
    )


@function_tool
def preparar_memorial_reparacion(pretensiones: str, rubros: str) -> str:
    """Estructura memorial de reparación integral."""
    return (
        "BORRADOR — Memorial reparación integral\n"
        f"Rubros:\n{rubros.strip()}\n"
        f"Pretensiones:\n{pretensiones.strip()}\n"
        "Incluir: destinatario, radicado, víctimas, fundamentos (KB reparacion).\n"
        "Validar con MemorialReparacionIntegral."
    )


@function_tool
def preparar_incidente_reparacion(etapa: str) -> str:
    """Estructura de incidente de reparación integral según etapa."""
    return (
        f"BORRADOR — Incidente reparación integral (etapa: {etapa.strip()})\n"
        "Verificar competencia y momento procesal en leer_kb_penal_victima('reparacion')."
    )


@function_tool
def evaluar_preacuerdo_victima(terminos: str) -> str:
    """Checklist de evaluación de preacuerdo desde interés de la víctima."""
    kb = _read_penal_kb(PENAL_VICTIMA_KB["negociacion"])
    return (
        f"EVALUACIÓN — Preacuerdo\nTérminos: {terminos.strip()}\n\n"
        f"{kb[:1000]}\n"
        "Completar InformePreacuerdoVictima para revisión del abogado."
    )


@function_tool
def evaluar_oposicion_principio_oportunidad(motivos: str) -> str:
    """Estructura para oposición al principio de oportunidad."""
    return (
        "BORRADOR — Oposición principio de oportunidad\n"
        f"Motivos: {motivos.strip()}\n"
        "Verificar procedencia y plazos en leer_kb_penal_victima('negociacion')."
    )


@function_tool
def evaluar_recurso_penal(decision: str, etapa: str) -> str:
    """Orientación sobre procedencia de recurso (no decisión automática)."""
    kb = _read_penal_kb(PENAL_VICTIMA_KB["recursos"])
    return (
        f"EVALUACIÓN — Recurso penal\nDecisión: {decision.strip()}\nEtapa: {etapa.strip()}\n\n"
        f"{kb[:1000]}"
    )


@function_tool
def preparar_recurso_penal(tipo: str, argumentos: str) -> str:
    """Estructura de memorial de recurso penal."""
    return (
        f"BORRADOR — Recurso ({tipo.strip()})\n"
        f"Argumentos:\n{argumentos.strip()}\n"
        "Incluir: destinatario, radicado, decisión impugnada, petición concreta."
    )


# Subconjuntos por agente
_ORCHESTRATOR_TOOLS = [
    detectar_etapa_penal,
    clasificar_objeto_penal,
    leer_playbook_penal_victima,
    leer_kb_penal_victima,
    listar_areas_derecho,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_INVESTIGACION_TOOLS = [
    leer_playbook_penal_victima,
    leer_kb_penal_victima,
    leer_area_derecho,
    preparar_denuncia_victima,
    preparar_peticion_fiscal,
    detectar_pruebas_faltantes_victima,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_GARANTIAS_TOOLS = [
    leer_playbook_proceso,
    leer_kb_penal_victima,
    preparar_audiencia_garantias,
    evaluar_medidas_proteccion_victima,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_CONOCIMIENTO_TOOLS = [
    leer_playbook_proceso,
    leer_kb_penal_victima,
    preparar_audiencia_preparatoria,
    preparar_juicio_oral,
    preparar_interrogatorio_victima,
    preparar_alegatos_victima,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_PRUEBA_TOOLS = [
    leer_kb_penal_victima,
    construir_teoria_probatoria_victima,
    generar_matriz_prueba,
    evaluar_objecion_prueba,
    detectar_pruebas_faltantes_victima,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_REPARACION_TOOLS = [
    leer_kb_penal_victima,
    leer_normas_clave,
    estimar_rubros_reparacion,
    preparar_memorial_reparacion,
    preparar_incidente_reparacion,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

_NEGOCIACION_TOOLS = [
    leer_kb_penal_victima,
    leer_normas_clave,
    evaluar_preacuerdo_victima,
    evaluar_oposicion_principio_oportunidad,
    buscar_en_conocimiento,
]

_RECURSOS_TOOLS = [
    leer_kb_penal_victima,
    leer_normas_clave,
    evaluar_recurso_penal,
    preparar_recurso_penal,
    buscar_en_conocimiento,
    buscar_en_expediente,
]

from src.agents.agent_names import (  # noqa: E402
    AGENTE_COORDINADOR_PENAL,
    SUBAGENTE_INVESTIGACION_VICTIMA,
    SUBAGENTE_PENAL_GARANTIAS,
    SUBAGENTE_PENAL_JUICIOS,
    SUBAGENTE_PENAL_NEGOCIACION,
    SUBAGENTE_PENAL_PRUEBAS,
    SUBAGENTE_PENAL_REPARACION,
    SUBAGENTE_PENAL_RECURSOS,
)

_PENAL_AGENT_TOOLS: dict[str, list] = {
    AGENTE_COORDINADOR_PENAL: _ORCHESTRATOR_TOOLS,
    SUBAGENTE_INVESTIGACION_VICTIMA: _INVESTIGACION_TOOLS,
    SUBAGENTE_PENAL_GARANTIAS: _GARANTIAS_TOOLS,
    SUBAGENTE_PENAL_JUICIOS: _CONOCIMIENTO_TOOLS,
    SUBAGENTE_PENAL_PRUEBAS: _PRUEBA_TOOLS,
    SUBAGENTE_PENAL_REPARACION: _REPARACION_TOOLS,
    SUBAGENTE_PENAL_NEGOCIACION: _NEGOCIACION_TOOLS,
    SUBAGENTE_PENAL_RECURSOS: _RECURSOS_TOOLS,
}


def get_penal_victima_tools(agent_name: str) -> list:
    """Devuelve el subconjunto de tools penal para un agente litigante."""
    return list(_PENAL_AGENT_TOOLS.get(agent_name, _ORCHESTRATOR_TOOLS))


def get_all_penal_tools() -> list:
    """Lista única de todas las tools penales (tests y registro)."""
    seen: set[int] = set()
    out: list = []
    for tools in _PENAL_AGENT_TOOLS.values():
        for t in tools:
            tid = id(t)
            if tid not in seen:
                seen.add(tid)
                out.append(t)
    return out
