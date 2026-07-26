"""Triage determinista unico: destino de agente + snapshot estructurado.

Fuente unica de enrutamiento para chat, planner y gate de alto riesgo
(evita dos routers divergentes — Supervisor / Centralized Tool Routing).
"""

from __future__ import annotations

import re

from src.agents.completeness import assess_completeness, infer_stage
from src.agents.schemas import TriageResult
from src.agents.urgency import assess_urgency
from src.storage.models import Expediente

POC_AGENT_ID = "coordinador_expediente_penal"

_TUTELA_RE = re.compile(
    r"\b(tutela|derecho fundamental|subsidiariedad|inmediatez)\b", re.I
)
_SEGUIMIENTO_RE = re.compile(
    r"\b(seguimiento|radicado|actuaci[oó]n|vencimiento|t[eé]rmino|inactividad)\b",
    re.I,
)
_AUDIENCIA_RE = re.compile(
    r"\b(audiencia|interrogatorio|contrainterrogatorio|juicio|alegato)\b", re.I
)
_EVIDENCIA_RE = re.compile(
    r"\b(evidencia|prueba|cadena de custodia|perit[oa]|testig)\b", re.I
)
_TIPICIDAD_RE = re.compile(
    r"\b(tipicidad|tipo penal|autor[ií]a|participaci[oó]n|dolo|culpa|"
    r"agravante|atenuante|conducta punible|delito)\b",
    re.I,
)
_RUTA906_RE = re.compile(
    r"\b(ley 906|imputaci[oó]n|acusaci[oó]n|preparatoria|control de garant[ií]as|"
    r"etapa procesal|oportunidad procesal|fiscal[ií]a)\b",
    re.I,
)
_VICTIMAS_RE = re.compile(
    r"\b(v[ií]ctima|revictimizaci[oó]n|reparaci[oó]n integral|"
    r"enfoque diferencial|derechos de la v[ií]ctima)\b",
    re.I,
)
_CRONOLOGIA_RE = re.compile(
    r"\b(cronolog[ií]a|linea de tiempo|hechos|narrativa factual|relato)\b", re.I
)
_REDACCION_RE = re.compile(
    r"\b(memorial|solicitud|recurso|derecho de petici[oó]n|redact|escrito|borrador)\b",
    re.I,
)
_CALIDAD_RE = re.compile(
    r"\b(calidad|verificar|auditar|alucinaci[oó]n|coherencia|confidencialidad)\b",
    re.I,
)
_OUT_OF_SCOPE_RE = re.compile(
    r"\b(civil|familia|societari[oa]|comercial|laboral|consumidor|contractual|"
    r"contrato|divorcio|custodia|alimentos|arrendamiento)\b",
    re.I,
)
_KNOWLEDGE_RE = re.compile(
    r"\b(ley 906|proceso penal|despacho penal|rutas penales)\b", re.I
)
_PROFILE_RE = re.compile(
    r"\b(perfil|experiencia|qu[ií]en eres|quien eres)\b", re.I
)
_PENAL_CONTEXT_PATTERNS = (
    _TUTELA_RE,
    _SEGUIMIENTO_RE,
    _AUDIENCIA_RE,
    _EVIDENCIA_RE,
    _TIPICIDAD_RE,
    _RUTA906_RE,
    _VICTIMAS_RE,
    _CRONOLOGIA_RE,
    _KNOWLEDGE_RE,
)

_DEST_TO_TAREA: dict[str, str] = {
    "analista_cronologia_hechos_penales": "analisis_factual",
    "analista_tipicidad_y_responsabilidad_penal": "tipicidad",
    "analista_ruta_procesal_ley906": "ruta_906",
    "analista_representacion_victimas": "representacion_victima",
    "gestor_evidencia_y_soporte_probatorio": "evidencia",
    "preparador_estrategico_audiencias_penales": "audiencia",
    "redactor_documentos_juridicos_penales": "redaccion",
    "gestor_seguimiento_procesal_penal": "seguimiento",
    "evaluador_derechos_fundamentales_tutela": "tutela_constitucional",
    "analista_calidad_juridica": "seguimiento",
    POC_AGENT_ID: "seguimiento",
}

HIGH_RISK_DESTINATIONS = frozenset(
    {
        "redactor_documentos_juridicos_penales",
        "evaluador_derechos_fundamentales_tutela",
    }
)


def has_penal_context(message: str) -> bool:
    return any(pattern.search(message or "") for pattern in _PENAL_CONTEXT_PATTERNS)


def is_non_penal_scope_request(message: str) -> bool:
    return bool(_OUT_OF_SCOPE_RE.search(message or "")) and not has_penal_context(
        message or ""
    )


def infer_destination_agent(message: str) -> str:
    """Unica funcion de destino: usada por chat, planner y gates."""
    if is_non_penal_scope_request(message):
        return POC_AGENT_ID
    if _CALIDAD_RE.search(message):
        return "analista_calidad_juridica"
    if _TUTELA_RE.search(message):
        return "evaluador_derechos_fundamentales_tutela"
    # La intención explícita de producir un escrito prevalece sobre términos
    # contextuales como "última actuación" o "radicado".
    if _REDACCION_RE.search(message):
        return "redactor_documentos_juridicos_penales"
    if _AUDIENCIA_RE.search(message):
        return "preparador_estrategico_audiencias_penales"
    if _EVIDENCIA_RE.search(message):
        return "gestor_evidencia_y_soporte_probatorio"
    if _TIPICIDAD_RE.search(message):
        return "analista_tipicidad_y_responsabilidad_penal"
    if _CRONOLOGIA_RE.search(message):
        return "analista_cronologia_hechos_penales"
    if _RUTA906_RE.search(message):
        return "analista_ruta_procesal_ley906"
    if _VICTIMAS_RE.search(message):
        return "analista_representacion_victimas"
    if _SEGUIMIENTO_RE.search(message):
        return "gestor_seguimiento_procesal_penal"
    if _PROFILE_RE.search(message):
        return POC_AGENT_ID
    if _KNOWLEDGE_RE.search(message):
        return "analista_ruta_procesal_ley906"
    return POC_AGENT_ID


def _summarize(message: str, limit: int = 240) -> str:
    normalized = " ".join((message or "").split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


_OPERATIONAL_HINT = re.compile(
    r"\b(redact|memorial|tutela|audiencia|tipicidad|cronolog|evidencia|"
    r"radicado|impulso|recurso|vencimiento|urgente)\w*",
    re.I,
)


def is_trivial_consultation(message: str, *, destination: str | None = None) -> bool:
    """Consultas donde no conviene interrumpir con escalamiento de urgencia."""
    dest = destination or infer_destination_agent(message)
    if is_non_penal_scope_request(message):
        return True
    if _PROFILE_RE.search(message or ""):
        return True
    if dest == POC_AGENT_ID and not _OPERATIONAL_HINT.search(message or ""):
        return True
    return False


def format_triage_sistema(triage: TriageResult) -> str:
    """Bloque pre-LLM con triage/urgencia/faltantes (el LLM no debe re-clasificar)."""
    faltantes = (
        ", ".join(triage.datos_faltantes_bloqueantes)
        if triage.datos_faltantes_bloqueantes
        else "(ninguno)"
    )
    motivos = (
        "; ".join(triage.motivos_urgencia) if triage.motivos_urgencia else "(ninguno)"
    )
    return (
        "[TRIAGE_SISTEMA — evaluación determinista; no re-clasificar]\n"
        f"- tipo_tarea: {triage.tipo_tarea}\n"
        f"- etapa_aparente: {triage.etapa_aparente}\n"
        f"- agente_destino: {triage.agente_destino}\n"
        f"- puede_continuar: {triage.puede_continuar}\n"
        f"- faltantes_bloqueantes: {faltantes}\n"
        f"- nivel_urgencia: {triage.nivel_urgencia}\n"
        f"- urgencia_preliminar: {triage.urgencia_preliminar}\n"
        f"- escalar_humano: {triage.escalar_humano}\n"
        f"- motivos_urgencia: {motivos}\n"
    )


def build_triage(
    message: str,
    *,
    expediente: Expediente | None = None,
    destination: str | None = None,
) -> TriageResult:
    """Construye TriageResult determinista (sin LLM) como contrato unico de ruteo."""
    dest = destination or infer_destination_agent(message)
    urgency = assess_urgency(message, expediente)
    fuera = is_non_penal_scope_request(message)
    tipo = "fuera_de_alcance" if fuera else _DEST_TO_TAREA.get(dest, "seguimiento")
    completeness = assess_completeness(
        message,
        destination=dest,
        expediente=expediente,
    )
    stage = completeness.etapa_aparente or infer_stage(message, expediente)
    return TriageResult(
        tipo_tarea=tipo,  # type: ignore[arg-type]
        etapa_aparente=stage,  # type: ignore[arg-type]
        agente_destino=dest,
        datos_faltantes_bloqueantes=list(completeness.faltantes),
        puede_continuar=completeness.puede_continuar,
        urgencia_preliminar=urgency.urgencia_preliminar,
        nivel_urgencia=urgency.nivel_urgencia,
        motivos_urgencia=list(urgency.motivos),
        escalar_humano=urgency.escalar_humano,
        accion_inmediata_urgencia=urgency.accion_inmediata_sugerida,
        resumen_triage=_summarize(message),
    )


def requires_execution_plan(destination: str) -> bool:
    return destination in HIGH_RISK_DESTINATIONS
