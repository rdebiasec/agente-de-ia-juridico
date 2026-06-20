"""Adaptador WhatsApp — Twilio webhook."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Form, Response

from src.config import get_settings
from src.gateway.router import InboundMessage, handle_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/webhook")
async def twilio_webhook(
    From: str = Form(...),
    Body: str = Form(""),
    ProfileName: str = Form(""),
):
    settings = get_settings()
    user_id = From.replace("whatsapp:", "")
    result = await handle_message(
        InboundMessage(channel="whatsapp", user_id=user_id, text=Body.strip() or "Hola")
    )

    text = result["text"]
    if result.get("pending_review") and settings.slack_bot_token:
        try:
            from slack_sdk.web.async_client import AsyncWebClient

            client = AsyncWebClient(token=settings.slack_bot_token)
            await client.chat_postMessage(
                channel=settings.slack_review_channel,
                text=(
                    f"*Revisión WhatsApp* — {ProfileName or user_id}\n"
                    f"> {Body[:200]}\n\n*Respuesta propuesta:*\n{text[:1500]}"
                ),
            )
            text = (
                "Su consulta fue recibida y está en revisión por el despacho. "
                "Le responderemos pronto."
                + "\n\n---\n*Mensaje automático — Fase 0*"
            )
        except Exception as e:
            logger.error("No se pudo enviar a Slack revisión: %s", e)

    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{_escape_xml(text[:1600])}</Message></Response>'
    return Response(content=twiml, media_type="application/xml")


def _escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
