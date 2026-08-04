"""Borrador de respuesta a la víctima (HITL) + filtro de calidad local."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.agents.guardrails import DISCLAIMER_TEXT, apply_output_guardrails
from src.storage import get_repository

_RADICADO_FAKE_RE = re.compile(
    r"\b(?:radicado|proceso)\s*(?:n[oº°\.]*\s*)?\d{10,}\b",
    re.I,
)
_SENTENCIA_FAKE_RE = re.compile(
    r"\b(?:sentencia|C-\d{3,4}|T-\d{3,4}|SU-\d{3,4})\b",
    re.I,
)
_PROMISE_RE = re.compile(
    r"\b(?:garantizamos|aseguramos\s+que\s+ganar[aá]|plazo\s+exacto\s+de\s+\d+\s+d[ií]as)\b",
    re.I,
)
_HARSH_RE = re.compile(
    r"\b(?:usted\s+mintió|es\s+culpable|merece\s+castigo|no\s+le\s+creemos)\b",
    re.I,
)


@dataclass
class DraftQuality:
    ok: bool
    flags: list[str]
    cleaned_text: str


def contextual_gerente_draft(
    inbound: str,
    *,
    lawyer_session_id: str,
) -> str:
    """Borrador contextual (sin LLM) usando expediente del desk."""
    excerpt = " ".join((inbound or "").split())[:500]
    exp = get_repository().get_expediente(lawyer_session_id)
    case_bits: list[str] = []
    if exp:
        if exp.radicado:
            case_bits.append(f"radicado que consta en expediente: {exp.radicado}")
        if exp.etapa_actual:
            case_bits.append(f"etapa aparente: {exp.etapa_actual}")
        if exp.rol_despacho:
            case_bits.append(f"rol del despacho: {exp.rol_despacho}")
    case_line = (
        "Datos del expediente que ya tenemos: " + "; ".join(case_bits) + "."
        if case_bits
        else "Aún no hay radicado/etapa confirmados en el expediente; no inventaré datos."
    )

    body = (
        "Como Coordinador del Caso, preparé esta respuesta para su revisión "
        "antes de enviarla a la víctima:\n\n"
        f"Recibimos su mensaje. {case_line}\n\n"
        "Le confirmamos que el despacho representa a víctimas en el proceso "
        "penal colombiano y que su consulta está en seguimiento interno. "
        "El abogado titular revisará esta respuesta antes de que usted la vea "
        "como comunicación formal del Gerente.\n\n"
        f"Sobre lo que nos cuenta («{excerpt}»), le pediremos —si hace falta— "
        "solo los datos mínimos para orientar la ruta (hechos, denuncia previa, "
        "medidas de protección). No prometemos resultados judiciales.\n\n"
        f"{DISCLAIMER_TEXT}"
    )
    return apply_output_guardrails(body, channel="web")


def quality_check_cliente_draft(text: str) -> DraftQuality:
    """Filtro liviano pre-bandeja: tono, no inventar, no promesas."""
    flags: list[str] = []
    cleaned = (text or "").strip()

    if _HARSH_RE.search(cleaned):
        flags.append("tono_riesgo_revictimizacion")
        cleaned = _HARSH_RE.sub("[ajuste de tono pendiente]", cleaned)

    # Radicados/sentencias solo se toleran si ya están en expediente; si el borrador
    # inventa números largos nuevos, marcar.
    if _RADICADO_FAKE_RE.search(cleaned):
        # No borramos automáticamente (puede ser el real del expediente); flag para abogado.
        flags.append("revisar_radicado_citado")
    if _SENTENCIA_FAKE_RE.search(cleaned):
        flags.append("revisar_cita_jurisprudencial")
    if _PROMISE_RE.search(cleaned):
        flags.append("promesa_resultado")
        cleaned = _PROMISE_RE.sub("orientaremos según el proceso", cleaned)

    if len(cleaned) < 40:
        flags.append("borrador_demasiado_corto")

    if DISCLAIMER_TEXT.lower() not in cleaned.lower():
        cleaned = apply_output_guardrails(cleaned, channel="web")

    return DraftQuality(ok=len(flags) == 0, flags=flags, cleaned_text=cleaned)


def build_outbound_proposal(
    inbound: str,
    *,
    lawyer_session_id: str,
) -> tuple[str, list[str]]:
    """Genera propuesta + flags de calidad para la bandeja del abogado."""
    draft = contextual_gerente_draft(inbound, lawyer_session_id=lawyer_session_id)
    quality = quality_check_cliente_draft(draft)
    return quality.cleaned_text, list(quality.flags)
