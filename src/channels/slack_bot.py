"""Adaptador Slack Bolt."""

from __future__ import annotations

import asyncio
import logging

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from src.channels.slack_plan import handle_slack_plan_message
from src.config import get_settings
from src.gateway.router import InboundMessage, handle_message

logger = logging.getLogger(__name__)


def create_slack_app() -> AsyncApp | None:
    settings = get_settings()
    if not settings.slack_bot_token or not settings.slack_signing_secret:
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

    return app


async def start_slack_socket_mode():
    settings = get_settings()
    app = create_slack_app()
    if not app:
        logger.warning("Slack no configurado — omitiendo Socket Mode")
        return
    handler = AsyncSocketModeHandler(app, settings.slack_bot_token)
    await handler.start_async()
