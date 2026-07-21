"""Notificación de borradores al abogado vía Slack (Block Kit + botones).

Si no hay `SLACK_BOT_TOKEN` configurado, las funciones son no-op y devuelven
None, de modo que el flujo web funcione igual sin Slack.
"""

from __future__ import annotations

import logging

from src.config import get_settings
from src.storage.models import Draft

logger = logging.getLogger(__name__)


def slack_habilitado() -> bool:
    return bool(get_settings().slack_bot_token)


def _bloques_revision(draft: Draft) -> list[dict]:
    cuerpo = draft.contenido.strip()
    if len(cuerpo) > 2800:
        cuerpo = cuerpo[:2800] + "\n…(truncado)"
    encabezado = (
        "*Borrador para revisión* · preparado por el equipo interno · presentado por el "
        f"coordinador del expediente · {draft.tipo}"
    )
    if draft.materia:
        encabezado += f" · {draft.materia}"
    return [
        {"type": "section", "text": {"type": "mrkdwn", "text": encabezado}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*{draft.titulo}*\n{cuerpo}"}},
        {
            "type": "actions",
            "block_id": f"draft::{draft.id}",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Aprobar"},
                    "style": "primary",
                    "action_id": "draft_aprobar",
                    "value": draft.id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Rechazar"},
                    "style": "danger",
                    "action_id": "draft_rechazar",
                    "value": draft.id,
                },
            ],
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"ID `{draft.id}` · sesión `{draft.session_id}`"}
            ],
        },
    ]


def notificar_texto(mensaje: str) -> str | None:
    """Publica un mensaje simple en el canal de revisión (p. ej. alertas de plazos)."""
    settings = get_settings()
    if not settings.slack_bot_token:
        return None
    try:
        from slack_sdk import WebClient

        client = WebClient(token=settings.slack_bot_token)
        resp = client.chat_postMessage(channel=settings.slack_review_channel, text=mensaje)
        return resp.get("ts")
    except Exception as exc:  # pragma: no cover - depende de red/credenciales
        logger.warning("No se pudo enviar alerta a Slack: %s", exc)
        return None


def notificar_borrador(draft: Draft) -> str | None:
    """Publica el borrador en el canal de revisión. Devuelve el ts del mensaje o None."""
    settings = get_settings()
    if not settings.slack_bot_token:
        return None
    try:
        from slack_sdk import WebClient

        client = WebClient(token=settings.slack_bot_token)
        resp = client.chat_postMessage(
            channel=settings.slack_review_channel,
            blocks=_bloques_revision(draft),
            text=f"Borrador para revisión: {draft.titulo}",
        )
        return resp.get("ts")
    except Exception as exc:  # pragma: no cover - depende de red/credenciales
        logger.warning("No se pudo notificar borrador a Slack: %s", exc)
        return None
