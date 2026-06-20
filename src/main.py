"""FastAPI — gateway principal."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.agents.runner import run_agent
from src.channels.whatsapp_webhook import router as whatsapp_router
from src.config import get_settings
from src.gateway.router import InboundMessage, handle_message
from src.validation.probes import generate_probes
from src.validation.rubric import CONNECTION_BLOCK, VALIDATION_BLOCKS, total_weight

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

_static_dir = get_settings().project_root / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")


@app.get("/")
async def chat_page():
    index = _static_dir / "index.html"
    if index.is_file():
        return FileResponse(index)
    return {"message": "Agente Jurídico API — use POST /chat"}


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


class GenerateProbesRequest(BaseModel):
    user_id: str = "web"
    blocks: list[str] | None = None
    probes_per_block: int = 2


@app.get("/validation/rubric")
async def validation_rubric():
    """Pesos y metadatos de la rúbrica Fase 0."""
    return {
        "total_weight": total_weight(),
        "connection": CONNECTION_BLOCK,
        "blocks": [
            {
                "id": b["id"],
                "title": b["title"],
                "weight": b["weight"],
            }
            for b in VALIDATION_BLOCKS
        ],
    }


@app.post("/validation/generate-probes")
async def validation_generate_probes(req: GenerateProbesRequest):
    try:
        return await generate_probes(
            user_id=req.user_id,
            blocks=req.blocks,
            probes_per_block=req.probes_per_block,
        )
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=429, detail=str(e)) from e


def main():
    import uvicorn

    settings = get_settings()
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.port, reload=False)


if __name__ == "__main__":
    main()
