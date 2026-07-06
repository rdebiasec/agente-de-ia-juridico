"""Extrae datos del expediente desde el chat (heurísticas, sin inventar)."""

from __future__ import annotations

import re

from src.gateway.expediente import expediente_store
from src.storage.models import MATERIAS

_RADICADO_RE = re.compile(
    r"\b(?:radicado\s*(?:interno|No\.?|n[uú]mero)?\s*)?"
    r"([A-Z]{0,5}-?\d{4,5}-?\d{2}-?\d{2,4}-?\d{4}-?\d{5,8}|\d{5}-\d{2}-\d{2}-\d{4}-\d{6,7})\b",
    re.IGNORECASE,
)
_CC_RE = re.compile(r"\bCC\s*([\d.]{6,12})\b", re.IGNORECASE)
_NIT_RE = re.compile(r"\bNIT\s*([\d.\-]{8,15})\b", re.IGNORECASE)
_ACCIONANTE_RE = re.compile(
    r"\b(?:accionante|actor|demandante|solicitante|soy|represento a)\s*[:\-]?\s*"
    r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,4})",
    re.IGNORECASE,
)
_ACCIONADO_RE = re.compile(
    r"\b(?:accionado|demandado|entidad|cementerio|empresa)\s*[:\-]?\s*"
    r"([A-ZÁÉÍÓÚÑ][^\n,.;]{3,80})",
    re.IGNORECASE,
)


def _collect_text(message: str, history: list[dict]) -> str:
    parts = [message or ""]
    for msg in history[-12:]:
        parts.append(str(msg.get("content", "")))
    return "\n".join(parts)


def _detect_materia(text: str) -> str | None:
    lower = text.lower()
    if any(
        w in lower
        for w in (
            "penal",
            "fiscalía",
            "fiscalia",
            "imputación",
            "imputacion",
            "ley 906",
            "víctima",
            "victima",
            "acción penal",
            "accion penal",
            "tutela",
            "derecho fundamental",
        )
    ):
        return "penal"
    return None


def _merge_partes(existing: list[dict], rol: str, nombre: str, doc: str | None = None) -> list[dict]:
    nombre = nombre.strip()
    if not nombre:
        return existing
    for p in existing:
        if p.get("rol") == rol and p.get("nombre", "").lower() == nombre.lower():
            if doc and not p.get("documento"):
                p["documento"] = doc
            return existing
    entry = {"rol": rol, "nombre": nombre}
    if doc:
        entry["documento"] = doc
    return [*existing, entry]


def sync_expediente_from_chat(
    session_id: str,
    message: str,
    history: list[dict],
    *,
    trace: dict | None = None,
) -> dict:
    """Actualiza el expediente con datos explícitos del mensaje e historial."""
    text = _collect_text(message, history)
    exp = expediente_store.get_or_create(session_id)
    cambios: list[str] = []

    materia = _detect_materia(text)
    if materia and materia in MATERIAS:
        if exp.materia != materia:
            exp.materia = materia
            cambios.append(f"materia={materia}")
        if "tutela" in text.lower() and exp.tipo_proceso != "tutela":
            exp.tipo_proceso = "tutela"
            cambios.append("tipo_proceso=tutela")

    radicados = _RADICADO_RE.findall(text)
    if radicados:
        rad = radicados[-1].strip()
        if exp.radicado != rad:
            exp.radicado = rad
            cambios.append(f"radicado={rad}")

    for match in _ACCIONANTE_RE.finditer(text):
        exp.partes = _merge_partes(exp.partes, "accionante", match.group(1).strip())
        cambios.append("parte:accionante")

    for match in _ACCIONADO_RE.finditer(text):
        exp.partes = _merge_partes(exp.partes, "accionado", match.group(1).strip())
        cambios.append("parte:accionado")

    # CC del accionante
    ccs = _CC_RE.findall(text)
    if ccs and exp.partes:
        for parte in exp.partes:
            if parte.get("rol") == "accionante" and not parte.get("documento"):
                parte["documento"] = f"CC {ccs[0]}"
                cambios.append("doc:accionante")
                break

    nits = _NIT_RE.findall(text)
    if nits and exp.partes:
        for parte in exp.partes:
            if parte.get("rol") == "accionado" and not parte.get("documento"):
                parte["documento"] = f"NIT {nits[0]}"
                cambios.append("doc:accionado")
                break

    if "derecho" in text.lower() and "vulnerad" in text.lower():
        if exp.etapa_actual != "tutela_en_preparacion":
            exp.etapa_actual = "tutela_en_preparacion"
            cambios.append("etapa=tutela_en_preparacion")

    if cambios:
        import time

        exp.actualizado_en = time.time()
        from src.storage import get_repository

        get_repository().save_expediente(exp)

    if trace is not None:
        if cambios:
            trace.setdefault("spans", []).append(
                {
                    "name": "Expediente: sincronización",
                    "kind": "context",
                    "status": "done",
                    "detail": f"Campos actualizados: {', '.join(sorted(set(cambios)))}.",
                    "at_ms": trace.get("timestamp") or 0,
                }
            )
            trace["expediente_updated"] = True
        else:
            trace.setdefault("spans", []).append(
                {
                    "name": "Expediente: sincronización",
                    "kind": "context",
                    "status": "pending",
                    "detail": "Sin datos nuevos estructurados en este turno.",
                    "at_ms": trace.get("timestamp") or 0,
                }
            )

    return {"cambios": cambios, "resumen": exp.resumen()}
