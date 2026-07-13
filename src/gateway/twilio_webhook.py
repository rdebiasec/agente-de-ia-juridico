"""Webhook de estado de entrega SMS (Twilio StatusCallback).

Verifica `X-Twilio-Signature` con el Auth Token. Sin credenciales Twilio
el endpoint responde 503.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from src.config import get_settings
from src.services.twilio_notify import handle_sms_status_callback, verify_twilio_request

logger = logging.getLogger(__name__)

router = APIRouter(tags=["twilio"])


def _public_request_url(request: Request) -> str:
    """URL absoluta que Twilio usó (respeta X-Forwarded-* detrás de Render)."""
    forwarded_proto = (request.headers.get("x-forwarded-proto") or request.url.scheme).split(",")[0].strip()
    forwarded_host = (request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc).split(
        ","
    )[0].strip()
    path = request.url.path
    query = request.url.query
    base = f"{forwarded_proto}://{forwarded_host}{path}"
    return f"{base}?{query}" if query else base


@router.post("/twilio/sms-status")
async def twilio_sms_status(request: Request):
    settings = get_settings()
    if not settings.twilio_auth_token:
        raise HTTPException(status_code=503, detail="Twilio no está configurado.")

    form = await request.form()
    params = {str(k): str(v) for k, v in form.items()}
    signature = request.headers.get("X-Twilio-Signature")
    url = _public_request_url(request)

    if not verify_twilio_request(url, params, signature):
        logger.warning("Firma Twilio inválida en /twilio/sms-status")
        raise HTTPException(status_code=401, detail="Firma de Twilio inválida.")

    result = handle_sms_status_callback(params)
    return {"ok": True, **result}
