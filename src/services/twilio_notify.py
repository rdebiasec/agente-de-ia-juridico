"""Alertas transaccionales por SMS (Twilio) para términos procesales.

Patrón alineado con Slack: si no hay credenciales Twilio, las funciones son
no-op. Para producción se recomienda Messaging Service (`TWILIO_MESSAGING_SERVICE_SID`).
"""

from __future__ import annotations

import logging
import os
import re
from datetime import date

from src.config import get_settings
from src.storage.models import Deadline

logger = logging.getLogger(__name__)

_E164 = re.compile(r"^\+[1-9]\d{1,14}$")


def twilio_habilitado() -> bool:
    settings = get_settings()
    tiene_credenciales = bool(settings.twilio_account_sid and settings.twilio_auth_token)
    tiene_origen = bool(settings.twilio_messaging_service_sid or settings.twilio_from_number)
    return tiene_credenciales and tiene_origen and bool(settings.twilio_alert_to)


def resolve_status_callback_url() -> str | None:
    """URL absoluta del StatusCallback (env explícita o RENDER_EXTERNAL_URL)."""
    settings = get_settings()
    if settings.twilio_status_callback:
        return settings.twilio_status_callback.rstrip("/")
    render_url = (os.environ.get("RENDER_EXTERNAL_URL") or "").strip().rstrip("/")
    if render_url:
        return f"{render_url}/twilio/sms-status"
    return None


def normalizar_e164(telefono: str, *, default_country: str = "CO") -> str | None:
    """Normaliza a E.164. Colombia (+57) si falta prefijo internacional."""
    raw = telefono.strip()
    if not raw:
        return None
    if raw.startswith("+"):
        return raw if _E164.match(raw) else None
    digits = re.sub(r"\D", "", raw)
    if default_country == "CO":
        if digits.startswith("57") and len(digits) == 12:
            candidato = f"+{digits}"
        elif len(digits) == 10:
            candidato = f"+57{digits}"
        else:
            return None
    else:
        candidato = f"+{digits}"
    return candidato if _E164.match(candidato) else None


def formatear_alerta_plazos(
    vencidos: list[Deadline],
    proximos: list[Deadline],
    *,
    referencia: date,
    max_lineas: int = 6,
) -> str:
    """Texto plano para Slack o SMS (transaccional, sin markdown)."""
    if not vencidos and not proximos:
        return ""
    lineas = ["Alerta de terminos procesales"]
    for d in vencidos[:max_lineas]:
        lineas.append(f"VENCIDO: {d.descripcion} (limite {d.fecha_limite})")
    restantes_cupo = max(0, max_lineas - len(vencidos))
    for d in proximos[:restantes_cupo]:
        dias = (d.fecha_limite - referencia).days if d.fecha_limite else 0
        lineas.append(f"Por vencer en {dias} dia(s): {d.descripcion} (limite {d.fecha_limite})")
    extra = len(vencidos) + len(proximos) - (len(lineas) - 1)
    if extra > 0:
        lineas.append(f"... y {extra} termino(s) mas")
    return "\n".join(lineas)


def notificar_texto_sms(mensaje: str, *, to: str | None = None) -> str | None:
    """Envía SMS transaccional. Devuelve el SID del mensaje o None."""
    settings = get_settings()
    destino = normalizar_e164(to or settings.twilio_alert_to or "")
    if not destino:
        return None
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        return None
    if not settings.twilio_messaging_service_sid and not settings.twilio_from_number:
        return None

    try:
        from twilio.rest import Client

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        params: dict = {"to": destino, "body": mensaje[:1600]}
        if settings.twilio_messaging_service_sid:
            params["messaging_service_sid"] = settings.twilio_messaging_service_sid
        else:
            params["from_"] = settings.twilio_from_number
        callback = resolve_status_callback_url()
        if callback:
            params["status_callback"] = callback

        message = client.messages.create(**params)
        return message.sid
    except Exception as exc:  # pragma: no cover - depende de red/credenciales
        logger.warning("No se pudo enviar alerta SMS via Twilio: %s", exc)
        return None


def verify_twilio_request(url: str, params: dict[str, str], signature: str | None) -> bool:
    """Valida X-Twilio-Signature con el Auth Token (helper oficial del SDK)."""
    settings = get_settings()
    if not settings.twilio_auth_token or not signature:
        return False
    try:
        from twilio.request_validator import RequestValidator

        validator = RequestValidator(settings.twilio_auth_token)
        return bool(validator.validate(url, params, signature))
    except Exception:
        logger.exception("Fallo al validar firma Twilio")
        return False


def handle_sms_status_callback(params: dict[str, str]) -> dict:
    """Registra el estado de entrega; no expone PII en logs."""
    message_sid = (params.get("MessageSid") or params.get("SmsSid") or "").strip()
    status = (params.get("MessageStatus") or params.get("SmsStatus") or "").strip().lower()
    error_code = (params.get("ErrorCode") or "").strip()

    if status in {"failed", "undelivered"}:
        logger.warning(
            "SMS Twilio no entregado sid=%s status=%s error=%s",
            message_sid or "unknown",
            status,
            error_code or "n/a",
        )
    else:
        logger.info("SMS Twilio sid=%s status=%s", message_sid or "unknown", status or "unknown")

    return {
        "message_sid": message_sid or None,
        "status": status or None,
        "error_code": error_code or None,
    }
