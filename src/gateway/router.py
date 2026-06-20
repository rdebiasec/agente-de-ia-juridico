"""Router unificado Slack/WhatsApp → agente."""

from __future__ import annotations

from dataclasses import dataclass

from src.agents.runner import run_agent
from src.gateway.session import session_store


@dataclass
class InboundMessage:
    channel: str  # slack | whatsapp
    user_id: str
    text: str
    thread_id: str | None = None


async def handle_message(msg: InboundMessage) -> dict:
    session_store.append(msg.channel, msg.user_id, "user", msg.text)
    result = await run_agent(msg.text, channel=msg.channel, session_id=f"{msg.channel}:{msg.user_id}")
    session_store.append(msg.channel, msg.user_id, "assistant", result["text"])
    return result
