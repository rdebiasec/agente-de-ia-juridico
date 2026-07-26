"""Notificación de borradores al abogado vía Slack (Block Kit + botones).

Si no hay `SLACK_BOT_TOKEN` configurado, las funciones son no-op y devuelven
None, de modo que el flujo web funcione igual sin Slack.
"""

from __future__ import annotations

import logging

from src.config import get_settings
from src.storage.models import Draft

logger = logging.getLogger(__name__)

DRAFT_EDIT_CALLBACK = "draft_editar_modal"
DRAFT_CONTENT_ACTION = "draft_contenido"
DRAFT_COMMENT_ACTION = "draft_comentario"


def slack_habilitado() -> bool:
    return bool(get_settings().slack_bot_token)


def _bloques_revision(draft: Draft) -> list[dict]:
    cuerpo = draft.contenido.strip()
    if len(cuerpo) > 2800:
        cuerpo = cuerpo[:2800] + "\n…(truncado)"
    encabezado = (
        "*Borrador para revisión* · preparado por el equipo interno · presentado por el "
        f"Gerente del Caso Penal · {draft.tipo}"
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
                    "text": {"type": "plain_text", "text": "Editar"},
                    "action_id": "draft_editar",
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


def _bloques_resultado(draft: Draft, *, estado_label: str) -> list[dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{estado_label}* · `{draft.id}` · {draft.titulo}\n"
                    f"Revisor: `{draft.revisor or 'n/a'}`"
                    + (f"\nComentario: {draft.comentario}" if draft.comentario else "")
                ),
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "El resultado también quedó registrado en la sesión de origen del chat.",
                }
            ],
        },
    ]


def build_edit_modal(draft: Draft) -> dict:
    """Vista modal para aprobar-con-edición desde Slack."""
    initial = (draft.contenido or "").strip()
    if len(initial) > 2900:
        initial = initial[:2900] + "\n…(truncado para edición; complete en web si necesita más)"
    return {
        "type": "modal",
        "callback_id": DRAFT_EDIT_CALLBACK,
        "private_metadata": draft.id,
        "title": {"type": "plain_text", "text": "Editar borrador"},
        "submit": {"type": "plain_text", "text": "Guardar"},
        "close": {"type": "plain_text", "text": "Cancelar"},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*`{draft.id}`* · {draft.titulo}",
                },
            },
            {
                "type": "input",
                "block_id": "contenido_block",
                "label": {"type": "plain_text", "text": "Contenido revisado"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": DRAFT_CONTENT_ACTION,
                    "multiline": True,
                    "initial_value": initial,
                },
            },
            {
                "type": "input",
                "block_id": "comentario_block",
                "optional": True,
                "label": {"type": "plain_text", "text": "Comentario (opcional)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": DRAFT_COMMENT_ACTION,
                    "multiline": False,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Qué cambió y por qué",
                    },
                },
            },
        ],
    }


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


def actualizar_mensaje_resultado(
    draft: Draft,
    *,
    channel: str | None,
    message_ts: str | None,
    estado_label: str,
) -> bool:
    """Quita botones del mensaje original y deja el resultado de la revisión."""
    settings = get_settings()
    if not settings.slack_bot_token or not channel or not message_ts:
        return False
    try:
        from slack_sdk import WebClient

        client = WebClient(token=settings.slack_bot_token)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text=f"{estado_label}: {draft.titulo}",
            blocks=_bloques_resultado(draft, estado_label=estado_label),
        )
        return True
    except Exception as exc:  # pragma: no cover
        logger.warning("No se pudo actualizar mensaje Slack del borrador: %s", exc)
        return False
