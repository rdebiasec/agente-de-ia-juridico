"""Triage determinista unico: destino de agente + snapshot estructurado.

Fuente unica de enrutamiento para chat, planner y gate de alto riesgo
(evita dos routers divergentes — Supervisor / Centralized Tool Routing).
"""

from __future__ import annotations

import re

from dataclasses import dataclass

from src.agents.completeness import CompletenessResult, assess_completeness, infer_stage
from src.agents.schemas import TriageResult
from src.agents.urgency import UrgencyResult, assess_urgency
from src.storage.models import Expediente

POC_AGENT_ID = "coordinador_caso"

# Materias de otros equipos Lexiatek (no este asistente penal-víctimas).
_OTHER_TEAM_SCOPE_RE = re.compile(
    r"\b(tutela|acci[oó]n\s+de\s+tutela|acci[oó]n\s+constitucional)\b",
    re.I,
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
# G03: sin "borrador"/"escrito"/"redact" sueltos (evitan plan_required por resumen).
_REDACCION_RE = re.compile(
    r"(?:"
    r"\b(?:memorial|solicitud|recurso|derecho de petici[oó]n)\b|"
    r"\bredact(?:ar|e|ame|emos)\b|"
    r"\bborrador\s+de\s+(?:memorial|solicitud|recurso|escrito)\b|"
    r"\bescrito\s+(?:de\s+)?(?:impulso|solicitud|memorial)\b"
    r")",
    re.I,
)
# G03: sin "verificar" suelto (evita robar tipicidad/cronología).
_CALIDAD_RE = re.compile(
    r"\b("
    r"calidad\s+jur[ií]dica|control\s+de\s+calidad|"
    r"auditar\s+(?:la\s+)?(?:salida|borrador|dictamen|respuesta)|"
    r"alucinaci[oó]n|coherencia\s+estrat[eé]gica|"
    r"verificar\s+(?:citas|jurisprudencia|normas|calidad|coherencia)"
    r")\b",
    re.I,
)
_OUT_OF_SCOPE_RE = re.compile(
    r"\b(civil|familia|societari[oa]|comercial|laboral|consumidor|contractual|"
    r"contrato|divorcio|custodia|alimentos|arrendamiento)\b",
    re.I,
)
_ANIMAL_SCOPE_RE = re.compile(
    r"\b("
    r"animal(?:es)?|mascota(?:s)?|gato(?:s)?|perro(?:s)?|"
    r"loro(?:s)?|caballo(?:s)?|yegua(?:s)?|burro(?:s)?|"
    r"vaca(?:s)?|ternero(?:s)?|conejo(?:s)?|h[aá]mster(?:s)?|"
    r"p[aá]jaro(?:s)?|ave(?:s)?|veterinari[oa]s?|zootecni[ae]|"
    r"maltrato\s+animal|protecci[oó]n\s+animal"
    r")\b",
    re.I,
)
_HUMAN_VICTIM_HINT_RE = re.compile(
    r"\b("
    r"v[ií]ctima(?:s)?(?:\s+humana(?:s)?)?|persona(?:s)?|cliente|"
    r"mujer(?:es)?|hombre(?:s)?|niñ[oa]s?|menor(?:es)?|"
    r"hija(?:s)?|hijo(?:s)?|esposa|esposo|compa[nñ]era|compa[nñ]ero|"
    r"madre|padre|hermana(?:s)?|hermano(?:s)?|familiar(?:es)?"
    r")\b",
    re.I,
)
# Postura aparente de conductor/investigado (no víctima) — despacho es penal-víctimas.
_INVESTIGADO_RE = re.compile(
    r"(?:"
    r"\batropell[eé]\b|"
    r"\bchoqu[eé]\b|"
    r"\bme\s+(?:van\s+a\s+)?imput(?:ar|an|aron)\b|"
    r"\bsoy\s+(?:el|la)\s+(?:sindicad[oa]|indagad[oa]|imputad[oa])\b|"
    r"\bme\s+acus(?:an|aron)\b|"
    r"\bnecesito\s+(?:un\s+)?abogado\s+de\s+defensa\b|"
    r"\bme\s+detuv(?:ieron|o)\b"
    r")",
    re.I,
)
_KNOWLEDGE_RE = re.compile(
    r"\b(ley 906|proceso penal|caso penal|despacho penal|rutas penales|"
    r"lesiones(?:\s+personales)?|homicidio|denuncia penal)\b",
    re.I,
)
_PROFILE_RE = re.compile(
    r"\b(perfil|experiencia|qu[ií]en eres|quien eres)\b", re.I
)
_PENAL_CONTEXT_PATTERNS = (
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
    "analista_cronologia_hechos": "analisis_factual",
    "analista_responsabilidad_tipicidad": "tipicidad",
    "analista_ruta_procesal": "ruta_906",
    "analista_representacion_victimas": "representacion_victima",
    "analista_evidencia": "evidencia",
    "analista_audiencias": "audiencia",
    "redactor_documentos_juridicos": "redaccion",
    "analista_seguimiento_procesal": "seguimiento",
    "analista_calidad_juridica": "seguimiento",
    POC_AGENT_ID: "seguimiento",
}

HIGH_RISK_DESTINATIONS = frozenset(
    {
        "redactor_documentos_juridicos",
    }
)


def has_penal_context(message: str) -> bool:
    return any(pattern.search(message or "") for pattern in _PENAL_CONTEXT_PATTERNS)


def is_animal_scope_request(message: str) -> bool:
    """True cuando la consulta es de mascota/animal y no ancla víctima humana.

    Si el mismo mensaje menciona víctima humana (p. ej. hija + mascota),
    no se clasifica como fuera de alcance por animal: el componente humano
    debe poder seguir en vía penal-víctimas.
    """
    text = message or ""
    if not _ANIMAL_SCOPE_RE.search(text):
        return False
    if _HUMAN_VICTIM_HINT_RE.search(text):
        return False
    return True


def is_other_team_scope_request(message: str) -> bool:
    """True si el pedido es de otro equipo Lexiatek (no este asistente)."""
    return bool(_OTHER_TEAM_SCOPE_RE.search(message or ""))


def is_non_penal_scope_request(message: str) -> bool:
    text = message or ""
    if is_animal_scope_request(text):
        return True
    return bool(_OUT_OF_SCOPE_RE.search(text)) and not has_penal_context(text)


def is_investigado_posture(message: str) -> bool:
    """True si el relato sugiere rol de conductor/investigado, no víctima."""
    return bool(_INVESTIGADO_RE.search(message or ""))


def infer_destination_agent(message: str) -> str:
    """Unica funcion de destino: usada por chat, planner y gates."""
    if (
        is_non_penal_scope_request(message)
        or is_investigado_posture(message)
        or is_other_team_scope_request(message)
    ):
        return POC_AGENT_ID
    # La intención explícita de producir un escrito prevalece sobre términos
    # contextuales como "última actuación" o "radicado".
    if _REDACCION_RE.search(message):
        return "redactor_documentos_juridicos"
    if _AUDIENCIA_RE.search(message):
        return "analista_audiencias"
    if _EVIDENCIA_RE.search(message):
        return "analista_evidencia"
    if _TIPICIDAD_RE.search(message):
        return "analista_responsabilidad_tipicidad"
    if _CRONOLOGIA_RE.search(message):
        return "analista_cronologia_hechos"
    if _RUTA906_RE.search(message):
        return "analista_ruta_procesal"
    if _VICTIMAS_RE.search(message):
        return "analista_representacion_victimas"
    if _SEGUIMIENTO_RE.search(message):
        return "analista_seguimiento_procesal"
    # Calidad después del fondo: evita que "verificar tipicidad" robe el destino (G03).
    if _CALIDAD_RE.search(message):
        return "analista_calidad_juridica"
    if _PROFILE_RE.search(message):
        return POC_AGENT_ID
    if _KNOWLEDGE_RE.search(message):
        return "analista_ruta_procesal"
    return POC_AGENT_ID


@dataclass(frozen=True)
class TriageBundle:
    """Triage + verificación ya calculada (G02 — una sola pass por turno)."""

    triage: TriageResult
    completeness: CompletenessResult
    urgency: UrgencyResult


def _summarize(message: str, limit: int = 240) -> str:
    normalized = " ".join((message or "").split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."


_OPERATIONAL_HINT = re.compile(
    r"\b(redact|memorial|audiencia|tipicidad|cronolog|evidencia|"
    r"radicado|impulso|recurso|vencimiento|urgente)\w*",
    re.I,
)


def is_trivial_consultation(message: str, *, destination: str | None = None) -> bool:
    """Consultas donde no conviene interrumpir con escalamiento de urgencia."""
    dest = destination or infer_destination_agent(message)
    if is_non_penal_scope_request(message) or is_investigado_posture(message):
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
    rol = getattr(triage, "rol_aparente", None) or "no_determinado"
    return (
        "[TRIAGE_SISTEMA — evaluación determinista; no re-clasificar]\n"
        f"- tipo_tarea: {triage.tipo_tarea}\n"
        f"- etapa_aparente: {triage.etapa_aparente}\n"
        f"- agente_destino: {triage.agente_destino}\n"
        f"- rol_aparente: {rol}\n"
        f"- puede_continuar: {triage.puede_continuar}\n"
        f"- faltantes_bloqueantes: {faltantes}\n"
        f"- nivel_urgencia: {triage.nivel_urgencia}\n"
        f"- urgencia_preliminar: {triage.urgencia_preliminar}\n"
        f"- escalar_humano: {triage.escalar_humano}\n"
        f"- motivos_urgencia: {motivos}\n"
    )


def build_triage_bundle(
    message: str,
    *,
    expediente: Expediente | None = None,
    destination: str | None = None,
) -> TriageBundle:
    """Triage + completeness + urgency en una sola pass (G02)."""
    dest = destination or infer_destination_agent(message)
    urgency = assess_urgency(message, expediente)
    fuera = (
        is_non_penal_scope_request(message)
        or is_investigado_posture(message)
        or is_other_team_scope_request(message)
    )
    tipo = "fuera_de_alcance" if fuera else _DEST_TO_TAREA.get(dest, "seguimiento")
    if is_investigado_posture(message):
        rol_aparente = "investigado_o_conductor"
    elif fuera:
        rol_aparente = "fuera_penal_victimas"
    else:
        rol_aparente = "victima_o_despacho"
    completeness = assess_completeness(
        message,
        destination=dest,
        expediente=expediente,
    )
    stage = completeness.etapa_aparente or infer_stage(message, expediente)
    triage = TriageResult(
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
        rol_aparente=rol_aparente,  # type: ignore[arg-type]
    )
    return TriageBundle(triage=triage, completeness=completeness, urgency=urgency)


def build_triage(
    message: str,
    *,
    expediente: Expediente | None = None,
    destination: str | None = None,
) -> TriageResult:
    """Construye TriageResult determinista (sin LLM) como contrato unico de ruteo."""
    return build_triage_bundle(
        message, expediente=expediente, destination=destination
    ).triage


def requires_execution_plan(destination: str) -> bool:
    return destination in HIGH_RISK_DESTINATIONS
