"""Deteccion unificada de PII en entradas/salidas del despacho."""

from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
_PHONE_RE = re.compile(
    r"\b(?:\+?57[\s-]?)?(?:3\d{2}|60\d)[\s-]?\d{3}[\s-]?\d{4}\b"
)
# Documento solo si aparece etiquetado (evita falsos positivos con radicados).
_DOCUMENT_RE = re.compile(
    r"\b(c[eé]dula|cc|nit|documento\s+de\s+identidad)\b.{0,20}\d{6,10}",
    re.I,
)
_ADDRESS_RE = re.compile(
    r"\b(direcci[oó]n|domicilio|residencia)\b\s*[:\-]?\s*.{3,100}",
    re.I,
)
_PROTECTED_NAME_RE = re.compile(
    r"\b(v[ií]ctima|menor(?:\s+de\s+edad)?|niñ[oa]|adolescente)\b"
    r"\s*(?:es|:|-)\s*([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'-]+"
    r"(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ'-]+){1,4})",
    re.I,
)

CONTACT_FLAGS = frozenset({"email", "phone"})
SENSITIVE_FLAGS = frozenset({"document_id", "address", "protected_name"})


def pii_flags(text: str) -> list[str]:
    """Clasifica contactos y datos sensibles del expediente.

    Los contactos no son por sí solos un motivo para destruir una respuesta.
    Documento, dirección y nombres etiquetados de víctimas/menores sí requieren
    enmascaramiento fuera de un flujo aprobado.
    """
    flags: list[str] = []
    if not text:
        return flags
    if _EMAIL_RE.search(text):
        flags.append("email")
    if _PHONE_RE.search(text):
        flags.append("phone")
    if _DOCUMENT_RE.search(text):
        flags.append("document_id")
    if _ADDRESS_RE.search(text):
        flags.append("address")
    if _PROTECTED_NAME_RE.search(text):
        flags.append("protected_name")
    return flags


def has_pii(text: str) -> bool:
    return bool(pii_flags(text))


def sensitive_pii_flags(text: str) -> list[str]:
    return [flag for flag in pii_flags(text) if flag in SENSITIVE_FLAGS]


def has_sensitive_pii(text: str) -> bool:
    return bool(sensitive_pii_flags(text))


def mask_pii(text: str) -> str:
    """Enmascara toda PII para previews, logs y mensajes de rechazo."""
    if not text:
        return text
    out = _EMAIL_RE.sub("[email]", text)
    out = _PHONE_RE.sub("[telefono]", out)
    out = _DOCUMENT_RE.sub(lambda m: f"{m.group(1)} [documento]", out)
    out = _ADDRESS_RE.sub(lambda m: f"{m.group(1)}: [direccion protegida]", out)
    out = _PROTECTED_NAME_RE.sub(lambda m: f"{m.group(1)}: [nombre protegido]", out)
    return out


def mask_sensitive_pii(text: str) -> str:
    """Enmascara PII de caso y conserva datos de contacto operativos."""
    if not text:
        return text
    out = _DOCUMENT_RE.sub(lambda m: f"{m.group(1)} [documento]", text)
    out = _ADDRESS_RE.sub(lambda m: f"{m.group(1)}: [direccion protegida]", out)
    return _PROTECTED_NAME_RE.sub(lambda m: f"{m.group(1)}: [nombre protegido]", out)
