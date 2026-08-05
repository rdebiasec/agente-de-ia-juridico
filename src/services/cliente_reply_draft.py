"""Borrador de respuesta a la víctima (HITL) + intake conversacional inmediato."""

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

_IMPATIENCE_RE = re.compile(
    r"\b(?:aja\s*y\s*ya|y\s*ya\??|hola\??|hay\s+alguien|me\s+escuchan|respuesta|"
    r"cu[aá]ndo\s+responden|siguen\s+ah[ií])\b",
    re.I,
)
_THREAT_RE = re.compile(r"\b(?:amenaz|hostig|persegu|intimid)\w*", re.I)
_VIF_RE = re.compile(
    r"\b(?:violencia\s+intrafamiliar|vif|pareja|expareja|esposo|esposa|"
    r"novio|novia|conviviente)\b",
    re.I,
)
_EVIDENCE_RE = re.compile(
    r"\b(?:evidencia|prueba|captura|whatsapp|chat|audio|video|testigo)\w*",
    re.I,
)
_MONEY_RE = re.compile(r"\b(?:sin\s+plata|no\s+tengo\s+dinero|gratis|costo|honorario)\b", re.I)
_RISK_RE = re.compile(
    r"\b(?:peligro|miedo|me\s+va\s+a\s+(?:matar|pegar)|riesgo|ahora\s+mismo)\b",
    re.I,
)


@dataclass
class DraftQuality:
    ok: bool
    flags: list[str]
    cleaned_text: str


def _first_name(display_name: str | None) -> str:
    raw = (display_name or "").strip()
    if not raw:
        return ""
    return raw.split()[0][:40]


def build_intake_visible_reply(
    inbound: str,
    *,
    display_name: str | None = None,
    prior_cliente_messages: int = 0,
) -> str:
    """
    Respuesta inmediata visible a la víctima: empatía + preguntas de intake.
    No da consejo jurídico concreto ni inventa radicados/normas.
    """
    text = (inbound or "").strip()
    name = _first_name(display_name)
    hello = f"{name}, " if name else ""

    if prior_cliente_messages >= 1 and _IMPATIENCE_RE.search(text) and len(text) < 80:
        return (
            f"{hello}aquí sigo con usted. Ya recibí su relato y estoy armando el caso "
            "con el despacho.\n\n"
            "Para avanzar ahora mismo, ¿me confirma estas tres cosas?\n"
            "1) ¿En qué ciudad ocurrieron los hechos?\n"
            "2) ¿Ya hay denuncia, querella o medida de protección? (sí/no; si sí, ante quién)\n"
            "3) ¿Hay riesgo actual para usted o su familia hoy?\n\n"
            "Mientras responde, el abogado revisa en paralelo la orientación jurídica. "
            "Si está en peligro inmediato, contacte a la policía (123) o a la línea 155."
        )

    focus = "lo que me cuenta"
    if _THREAT_RE.search(text):
        focus = "las amenazas / el hostigamiento que describe"
    elif _VIF_RE.search(text):
        focus = "la situación de violencia que describe"

    bits: list[str] = [
        f"{hello}gracias por confiarme su situación. Leí con atención {focus}.",
        "Voy a acompañarle paso a paso: primero reunimos lo esencial; "
        "el abogado del despacho valida la orientación jurídica antes de cualquier "
        "actuación formal.",
    ]

    if _RISK_RE.search(text):
        bits.append(
            "Si en este momento está en peligro, priorice su seguridad: "
            "policía 123 o línea 155."
        )

    if _EVIDENCE_RE.search(text):
        bits.append(
            "Bien que conserve evidencia (chats, audios, capturas). "
            "No la borre; más adelante le diremos cómo organizarla."
        )

    if _MONEY_RE.search(text):
        bits.append(
            "Entiendo la preocupación por recursos. Aquí no le pedimos pago para "
            "esta orientación inicial; el despacho le dirá con claridad qué sigue."
        )

    bits.append("Para ayudarle bien, ¿me puede responder esto?")
    questions: list[str] = [
        "1) ¿Cuándo fue el último hecho (fecha aproximada) y en qué ciudad?",
        "2) ¿Ya denunció o solicitó protección? Si sí, ¿ante qué autoridad?",
    ]
    if _THREAT_RE.search(text) or _EVIDENCE_RE.search(text):
        questions.append(
            "3) ¿Qué pruebas tiene a la mano (WhatsApp, audios, testigos) y desde cuándo?"
        )
    else:
        questions.append(
            "3) ¿Hay riesgo actual para usted o personas a su cargo?"
        )
    bits.append("\n".join(questions))
    bits.append(
        "Escríbame con lo que tenga; no necesita un relato perfecto. "
        "Estoy aquí para seguir la conversación."
    )
    return "\n\n".join(bits)


def contextual_gerente_draft(
    inbound: str,
    *,
    lawyer_session_id: str,
) -> str:
    """Borrador HITL para el abogado (orientación más completa; no visible aún)."""
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
        "Propuesta de orientación jurídica para aprobación del abogado "
        "(la víctima ya recibió un mensaje de intake conversacional):\n\n"
        f"{case_line}\n\n"
        f"Relato de la víctima («{excerpt}»).\n\n"
        "Borrador sugerido para la víctima (editable):\n"
        "— Reconocer el relato y la urgencia percibida sin revictimizar.\n"
        "— Pedir solo datos faltantes (fecha, ciudad, denuncia previa, riesgo actual, prueba).\n"
        "— Orientar de forma preliminar la vía penal-víctimas (sin tipicidad definitiva "
        "ni promesas de resultado).\n"
        "— Si hay riesgo inmediato: reforzar 123 / línea 155.\n"
        "— Cerrar invitando a seguir el diálogo y a conservar evidencia.\n\n"
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

    if _RADICADO_FAKE_RE.search(cleaned):
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
    """Genera propuesta HITL + flags de calidad para la bandeja del abogado."""
    draft = contextual_gerente_draft(inbound, lawyer_session_id=lawyer_session_id)
    quality = quality_check_cliente_draft(draft)
    return quality.cleaned_text, list(quality.flags)
