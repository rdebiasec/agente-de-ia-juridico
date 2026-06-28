"""Guardrails legales — supervisión humana."""

import re

DISCLAIMER_TEXT = "Borrador informativo — requiere revisión y aprobación del abogado."
DISCLAIMER = f"\n\n---\n*{DISCLAIMER_TEXT}*"

_DISCLAIMER_BLOCK_RE = re.compile(
    rf"\n*\s*---\s*\n?\s*\*?{re.escape(DISCLAIMER_TEXT)}\*?\s*",
    re.IGNORECASE,
)
_DISCLAIMER_LINE_RE = re.compile(
    rf"\n*\s*\*?{re.escape(DISCLAIMER_TEXT)}\*?\s*",
    re.IGNORECASE,
)
_PHASE_DRAFT_RE = re.compile(r"\n*\s*Fase\s*\d+\s*·\s*Borrador\s*", re.IGNORECASE)

FASE1_PLUS_KEYWORDS = re.compile(
    r"\b("
    r"contrato|redactar|demanda|recurso|riesgo|estrategia|teor[ií]a del caso|"
    r"correo corporativo|escrito|prueba faltante|debilidad|civil o penal|"
    r"solicitud|excepci[oó]n"
    r")\b",
    re.IGNORECASE,
)

FASE2_3_KEYWORDS = re.compile(
    r"\b("
    r"tutela|memorial|concepto jur[ií]dico|radicaci[oó]n|rama judicial|"
    r"radicado|seguimiento procesal|seguimiento mensual|informe mensual|alertas autom[aá]ticas|"
    r"entrevista|fiscal[ií]a|juez|impulso procesal|expediente|audiencia|accionante|accionado"
    r")\b",
    re.IGNORECASE,
)

DRAFT_REVIEW_INTENT = re.compile(
    r"\b("
    r"redact|contrato|escrito|recurso|solicitud|excepci[oó]n|correo|mensaje profesional|"
    r"estrategia|riesgo|teor[ií]a del caso"
    r")\w*",
    re.IGNORECASE,
)


def check_input(text: str) -> tuple[bool, str | None]:
    """Valida entrada. Retorna (ok, mensaje_error)."""
    if len(text) > 8000:
        return False, "Mensaje demasiado largo. Resuma su consulta."
    return True, None


def _phase_block_message(active_phase: int) -> str:
    if active_phase <= 0:
        return (
            "Esa capacidad pertenece a una fase posterior del proyecto (Fase 1, 2 o 3) "
            "y aún no está activa. En Fase 0 solo puedo orientar sobre el perfil del "
            "despacho y las áreas del derecho en nuestra base de conocimiento."
        )
    if active_phase == 1:
        return (
            "Esa capacidad pertenece a una fase posterior del proyecto (Fase 2 o 3) "
            "y aún no está activa. En Fase 1 puedo apoyar consulta, análisis de riesgos "
            "y redacción básica dentro del alcance habilitado."
        )
    return None


def check_phase_scope(text: str, active_phase: int | None = None) -> str | None:
    """Detecta solicitudes fuera de alcance según la fase activa."""
    if active_phase is None:
        from src.config import get_settings

        active_phase = get_settings().active_phase

    if active_phase <= 0 and FASE1_PLUS_KEYWORDS.search(text):
        return _phase_block_message(active_phase)
    if active_phase == 1 and FASE2_3_KEYWORDS.search(text):
        return _phase_block_message(active_phase)
    return None


def apply_output_guardrails(text: str, channel: str = "slack") -> str:
    """Añade un único disclaimer y normaliza salida."""
    normalized = text or ""
    normalized = _DISCLAIMER_BLOCK_RE.sub("\n", normalized)
    normalized = _DISCLAIMER_LINE_RE.sub("\n", normalized)
    normalized = _PHASE_DRAFT_RE.sub("\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return normalized + DISCLAIMER


def needs_human_review(text: str, channel: str, user_message: str = "") -> bool:
    """Determina cuándo la salida debe quedar pendiente de revisión humana."""
    from src.config import get_settings

    settings = get_settings()
    if channel == "whatsapp" and settings.require_human_review_whatsapp:
        return True

    if settings.active_phase >= 1 and settings.require_human_review_web:
        candidate = f"{user_message}\n{text}".strip()
        if channel in {"web", "api", "slack"} and DRAFT_REVIEW_INTENT.search(candidate):
            return True

    return False
