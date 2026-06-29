"""Router unificado → agente con sesión multi-turno persistida."""

from __future__ import annotations

from dataclasses import dataclass

from src.agents.runner import run_agent
from src.gateway.trace import trace_store


@dataclass
class InboundMessage:
    channel: str  # slack | web
    user_id: str
    text: str
    thread_id: str | None = None


async def handle_message(msg: InboundMessage) -> dict:
    session_id = f"{msg.channel}:{msg.user_id}"
    result = await run_agent(
        msg.text,
        channel=msg.channel,
        session_id=session_id,
        user_id=msg.user_id,
    )
    if result.get("trace"):
        trace_store.add(session_id, result["trace"])
    return result
