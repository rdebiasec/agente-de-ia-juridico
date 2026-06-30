"""Alertas transaccionales por SMS (Twilio) para términos procesales.

Patrón alineado con Slack: si no hay credenciales Twilio, las funciones son
no-op. Para producción se recomienda Messaging Service (`TWILIO_MESSAGING_SERVICE_SID`).
"""

from __future__ import annotations

import logging
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
        if settings.twilio_status_callback:
            params["status_callback"] = settings.twilio_status_callback

        message = client.messages.create(**params)
        return message.sid
    except Exception as exc:  # pragma: no cover - depende de red/credenciales
        logger.warning("No se pudo enviar alerta SMS via Twilio: %s", exc)
        return None
