"""Guardrails legales — supervisión humana.

En el modelo de firma virtual todas las capacidades están activas; los
guardrails ya no bloquean por fases, solo aseguran el disclaimer único,
la validación básica de entrada y la marca de revisión humana.
"""

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

# Intenciones accionables que deben quedar pendientes de aprobación del abogado.
DRAFT_REVIEW_INTENT = re.compile(
    r"\b("
    r"redact|proyect|escrito|recurso|solicitud|correo|mensaje profesional|"
    r"memorial|tutela|concepto|estrategia|riesgo|teor[ií]a del caso|"
    r"seguimiento|informe|radicaci[oó]n|audiencia|interrogatorio|entrevista"
    r")\w*",
    re.IGNORECASE,
)
_OUT_OF_SCOPE_RE = re.compile(r"fuera de alcance penal[- ]v[íi]ctimas", re.IGNORECASE)


def check_input(text: str) -> tuple[bool, str | None]:
    """Valida entrada. Retorna (ok, mensaje_error)."""
    if len(text) > 8000:
        return False, "Mensaje demasiado largo. Resuma su consulta."
    return True, None


def check_phase_scope(text: str, active_phase: int | None = None) -> str | None:
    """Compatibilidad histórica: en el modelo de firma no se bloquea por fases."""
    return None


def apply_output_guardrails(text: str, channel: str = "web") -> str:
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

    if _OUT_OF_SCOPE_RE.search(text or ""):
        return False

    settings = get_settings()
    if settings.require_human_review_web:
        candidate = f"{user_message}\n{text}".strip()
        if channel in {"web", "api", "slack"} and DRAFT_REVIEW_INTENT.search(candidate):
            return True

    return False
