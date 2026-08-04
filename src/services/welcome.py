"""Saludo de bienvenida del escritorio del abogado (TZ del despacho).

Zona horaria: DESPACHO_TZ / AGENT_TZ (default America/Bogota).
America/New_York = Eastern (Orlando, Florida, observa Eastern).
Bogotá vs Orlando se refinará con más detalle más adelante.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.config import Settings, get_settings

logger = logging.getLogger(__name__)

DEFAULT_DESPACHO_TZ = "America/Bogota"
# Orlando, FL observa Eastern → America/New_York (DST incluido).
SUPPORTED_DESPACHO_TZS = frozenset({"America/Bogota", "America/New_York"})

WELCOME_DISPLAY_NAME = "Coordinador del Caso"


def normalize_despacho_tz(raw: str | None) -> str:
    """Valida TZ; si es inválida, cae a America/Bogota."""
    candidate = (raw or "").strip() or DEFAULT_DESPACHO_TZ
    if candidate not in SUPPORTED_DESPACHO_TZS:
        try:
            ZoneInfo(candidate)
        except ZoneInfoNotFoundError:
            logger.warning(
                "DESPACHO_TZ inválida %r; usando %s",
                candidate,
                DEFAULT_DESPACHO_TZ,
            )
            return DEFAULT_DESPACHO_TZ
        # TZ IANA válida pero no listada: permitir (futuro) con aviso.
        logger.info(
            "DESPACHO_TZ %r no está en el set preferido %s; se usa igual.",
            candidate,
            sorted(SUPPORTED_DESPACHO_TZS),
        )
    return candidate


def resolve_despacho_tz(settings: Settings | None = None) -> str:
    """AGENT_TZ (si existe) tiene prioridad sobre DESPACHO_TZ / settings.despacho_tz."""
    settings = settings or get_settings()
    override = (os.environ.get("AGENT_TZ") or "").strip()
    raw = override or (settings.despacho_tz or "").strip() or DEFAULT_DESPACHO_TZ
    return normalize_despacho_tz(raw)


def greeting_for_hour(hour: int) -> str:
    """Saludo español por hora local del despacho.

    - buenos días: 5:00–11:59
    - buenas tardes: 12:00–18:59
    - buenas noches: 19:00–4:59
    """
    if 5 <= hour <= 11:
        return "Buenos días"
    if 12 <= hour <= 18:
        return "Buenas tardes"
    return "Buenas noches"


def lawyer_welcome_payload(
    *,
    settings: Settings | None = None,
    now: datetime | None = None,
    tz_name: str | None = None,
) -> dict[str, str | int]:
    """Payload para el bubble de bienvenida del desk abogado."""
    tz = normalize_despacho_tz(tz_name) if tz_name else resolve_despacho_tz(settings)
    try:
        zone = ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        tz = DEFAULT_DESPACHO_TZ
        zone = ZoneInfo(tz)

    local_now = now.astimezone(zone) if now is not None else datetime.now(zone)
    greeting = greeting_for_hour(local_now.hour)
    message = (
        f"{greeting}. Soy el Coordinador del Caso, "
        "asistente de IA penal del despacho."
    )
    return {
        "display_name": WELCOME_DISPLAY_NAME,
        "message": message,
        "greeting": greeting,
        "tz": tz,
        "local_hour": local_now.hour,
    }
