"""Adaptador Slack Bolt (Socket Mode).

Requiere SLACK_BOT_TOKEN (xoxb-…), SLACK_APP_TOKEN (xapp-…, connections:write)
y SLACK_SIGNING_SECRET. Docs: https://docs.slack.dev/tools/bolt-python/concepts/socket-mode
"""

from __future__ import annotations

import logging

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from src.channels.slack_plan import handle_slack_plan_message
from src.channels.slack_status import mark_slack_socket_started
from src.config import get_settings
from src.gateway.router import InboundMessage, handle_message
from src.gateway.slack_interactivity import (
    SlackAuthError,
    aplicar_accion_borrador,
    aplicar_edicion_borrador,
    ensure_slack_approver,
)
from src.hitl.drafts import TransicionInvalida
from src.hitl.slack_review import (
    DRAFT_COMMENT_ACTION,
    DRAFT_CONTENT_ACTION,
    DRAFT_EDIT_CALLBACK,
    build_edit_modal,
)
from src.storage import get_repository

logger = logging.getLogger(__name__)


def create_slack_app() -> AsyncApp | None:
    settings = get_settings()
    if not settings.slack_bot_token or not settings.slack_signing_secret:
        logger.warning(
            "Slack incompleto: faltan SLACK_BOT_TOKEN y/o SLACK_SIGNING_SECRET — omitiendo Bolt"
        )
        return None

    app = AsyncApp(
        token=settings.slack_bot_token,
        signing_secret=settings.slack_signing_secret,
    )

    async def _dispatch(text: str, user: str, say, thread_ts: str | None) -> None:
        handled = await handle_slack_plan_message(
            text=text,
            user_id=user,
            say=say,
            thread_ts=thread_ts,
        )
        if handled:
            return
        result = await handle_message(
            InboundMessage(channel="slack", user_id=user, text=text or "Hola")
        )
        await say(result["text"], thread_ts=thread_ts)

    @app.event("app_mention")
    async def on_mention(event, say, client):
        text = event.get("text", "").split(">", 1)[-1].strip()
        user = event.get("user", "unknown")
        await _dispatch(text, user, say, event.get("ts"))

    @app.message("")
    async def on_message(message, say):
        if message.get("subtype"):
            return
        text = message.get("text", "")
        if not text:
            return
        user = message.get("user", "unknown")
        thread_ts = message.get("thread_ts") or message.get("ts")
        await _dispatch(text, user, say, thread_ts)

    async def _on_draft_action(body, ack, respond):
        await ack()
        actions = body.get("actions") or []
        if not actions:
            return
        action = actions[0]
        try:
            revisor = ensure_slack_approver(body.get("user"))
        except SlackAuthError as exc:
            await respond(text=f":no_entry: {exc}", replace_original=False)
            return
        channel = (body.get("channel") or {}).get("id")
        message_ts = (body.get("message") or {}).get("ts")
        texto = aplicar_accion_borrador(
            action_id=action.get("action_id"),
            draft_id=action.get("value"),
            revisor=revisor,
            channel=channel,
            message_ts=message_ts,
        )
        if texto:
            await respond(text=texto, replace_original=False)

    @app.action("draft_aprobar")
    async def on_draft_aprobar(body, ack, respond):
        await _on_draft_action(body, ack, respond)

    @app.action("draft_rechazar")
    async def on_draft_rechazar(body, ack, respond):
        await _on_draft_action(body, ack, respond)

    @app.action("draft_editar")
    async def on_draft_editar(body, ack, client, respond):
        await ack()
        try:
            ensure_slack_approver(body.get("user"))
        except SlackAuthError as exc:
            await respond(text=f":no_entry: {exc}", replace_original=False)
            return
        actions = body.get("actions") or []
        if not actions:
            return
        draft_id = actions[0].get("value")
        draft = get_repository().get_draft(draft_id) if draft_id else None
        if draft is None:
            await respond(
                text=f":warning: Borrador {draft_id} no encontrado.",
                replace_original=False,
            )
            return
        trigger_id = body.get("trigger_id")
        if not trigger_id:
            await respond(text=":warning: No pude abrir el editor.", replace_original=False)
            return
        await client.views_open(trigger_id=trigger_id, view=build_edit_modal(draft))

    @app.view(DRAFT_EDIT_CALLBACK)
    async def on_draft_edit_submit(ack, body, view):
        try:
            revisor = ensure_slack_approver(body.get("user"))
        except SlackAuthError as exc:
            await ack(
                response_action="errors",
                errors={"contenido_block": str(exc)},
            )
            return

        draft_id = str(view.get("private_metadata") or "").strip()
        values = (view.get("state") or {}).get("values") or {}
        contenido = (
            ((values.get("contenido_block") or {}).get(DRAFT_CONTENT_ACTION) or {}).get(
                "value"
            )
            or ""
        ).strip()
        comentario = (
            ((values.get("comentario_block") or {}).get(DRAFT_COMMENT_ACTION) or {}).get(
                "value"
            )
            or ""
        ).strip() or None
        if not draft_id or not contenido:
            await ack(
                response_action="errors",
                errors={"contenido_block": "El contenido no puede estar vacío."},
            )
            return
        try:
            aplicar_edicion_borrador(
                draft_id,
                revisor=revisor,
                nuevo_contenido=contenido,
                comentario=comentario,
            )
        except KeyError:
            await ack(
                response_action="errors",
                errors={"contenido_block": "Borrador no encontrado."},
            )
            return
        except TransicionInvalida as exc:
            await ack(
                response_action="errors",
                errors={"contenido_block": str(exc)},
            )
            return
        await ack(response_action="clear")

    return app


async def start_slack_socket_mode():
    settings = get_settings()
    app = create_slack_app()
    if not app:
        logger.warning("Slack no configurado — omitiendo Socket Mode")
        mark_slack_socket_started(False)
        return
    if not settings.slack_app_token:
        logger.warning(
            "SLACK_APP_TOKEN ausente — Socket Mode requiere token xapp-… "
            "(docs.slack.dev Socket Mode). Usar xapp- con connections:write, "
            "no el bot token xoxb- (falla con not_allowed_token_type)."
        )
        mark_slack_socket_started(False)
        return
    handler = AsyncSocketModeHandler(app, settings.slack_app_token)
    logger.info("Slack Socket Mode: conectando con SLACK_APP_TOKEN (xapp-…)")
    try:
        mark_slack_socket_started(True)
        await handler.start_async()
    except Exception:
        mark_slack_socket_started(False)
        logger.exception("Slack Socket Mode: conexión fallida")
        raise
