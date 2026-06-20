"""FastAPI — gateway principal."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from src.agents.runner import run_agent
from src.channels.whatsapp_webhook import router as whatsapp_router
from src.config import get_settings
from src.gateway.router import InboundMessage, handle_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    slack_task = None
    if settings.slack_bot_token and settings.slack_signing_secret:
        try:
            from src.channels.slack_bot import start_slack_socket_mode

            slack_task = asyncio.create_task(start_slack_socket_mode())
            logger.info("Slack Socket Mode iniciado")
        except Exception as e:
            logger.warning("Slack Socket Mode no iniciado: %s", e)
    yield
    if slack_task:
        slack_task.cancel()


app = FastAPI(title="Agente Jurídico", version="0.1.0", lifespan=lifespan)
app.include_router(whatsapp_router)


class ChatRequest(BaseModel):
    message: str
    channel: str = "api"
    user_id: str = "test"


class ChatResponse(BaseModel):
    text: str
    agent: str
    pending_review: bool = False


@app.get("/health")
async def health():
    settings = get_settings()
    return {
        "status": "ok",
        "fase_activa": settings.active_phase,
        "openai_configured": bool(settings.openai_api_key),
        "slack_configured": bool(settings.slack_bot_token),
        "whatsapp_configured": bool(settings.twilio_account_sid),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = await handle_message(
        InboundMessage(channel=req.channel, user_id=req.user_id, text=req.message)
    )
    return ChatResponse(**{k: result[k] for k in ("text", "agent", "pending_review") if k in result})


def main():
    import uvicorn

    settings = get_settings()
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=False)


if __name__ == "__main__":
    main()
