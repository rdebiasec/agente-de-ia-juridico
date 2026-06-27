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
_PHASE_DRAFT_RE = re.compile(r"\n*\s*Fase\s*0\s*·\s*Borrador\s*", re.IGNORECASE)

FASE1_KEYWORDS = re.compile(
    r"\b(contrato|tutela|memorial|redactar|demanda|recurso|riesgo|estrategia|"
    r"teor[ií]a del caso|correo corporativo)\b",
    re.IGNORECASE,
)

CAPACIDAD_NO_ACTIVA = (
    "Esa capacidad pertenece a una fase posterior del proyecto (Fase 1, 2 o 3) "
    "y aún no está activa. En Fase 0 solo puedo orientar sobre el perfil del "
    "despacho y las áreas del derecho en nuestra base de conocimiento."
)


def check_input(text: str) -> tuple[bool, str | None]:
    """Valida entrada. Retorna (ok, mensaje_error)."""
    if len(text) > 8000:
        return False, "Mensaje demasiado largo. Resuma su consulta."
    return True, None


def check_phase_scope(text: str) -> str | None:
    """Detecta solicitudes fuera de Fase 0."""
    if FASE1_KEYWORDS.search(text):
        return CAPACIDAD_NO_ACTIVA
    return None


def apply_output_guardrails(text: str, channel: str = "slack") -> str:
    """Añade un único disclaimer y normaliza salida."""
    normalized = text or ""
    normalized = _DISCLAIMER_BLOCK_RE.sub("\n", normalized)
    normalized = _DISCLAIMER_LINE_RE.sub("\n", normalized)
    normalized = _PHASE_DRAFT_RE.sub("\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return normalized + DISCLAIMER


def needs_human_review(text: str, channel: str) -> bool:
    """WhatsApp externo requiere revisión antes de enviar al cliente."""
    from src.config import get_settings

    settings = get_settings()
    if channel == "whatsapp" and settings.require_human_review_whatsapp:
        return True
    return False
