"""Webhook de interactividad de Slack para aprobar/rechazar borradores.

Verifica la firma con `SLACK_SIGNING_SECRET`. Botones definidos en
`src/hitl/slack_review.py` (action_id `draft_aprobar` / `draft_rechazar`).
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, Request

from src.config import get_settings
from src.hitl import drafts as hitl
from src.hitl.drafts import TransicionInvalida

logger = logging.getLogger(__name__)

router = APIRouter()


def _verificar_firma(body: bytes, timestamp: str | None, signature: str | None, secret: str) -> bool:
    try:
        from slack_sdk.signature import SignatureVerifier

        verifier = SignatureVerifier(signing_secret=secret)
        return verifier.is_valid(body=body, timestamp=timestamp or "", signature=signature or "")
    except Exception:  # pragma: no cover - dependencias/entorno
        logger.exception("Fallo al verificar firma de Slack")
        return False


@router.post("/slack/interactivity")
async def slack_interactivity(request: Request):
    settings = get_settings()
    if not settings.slack_signing_secret:
        raise HTTPException(status_code=503, detail="Slack no está configurado.")

    raw = await request.body()
    ts = request.headers.get("X-Slack-Request-Timestamp")
    sig = request.headers.get("X-Slack-Signature")
    if not _verificar_firma(raw, ts, sig, settings.slack_signing_secret):
        raise HTTPException(status_code=401, detail="Firma de Slack inválida.")

    form = await request.form()
    payload_raw = form.get("payload")
    if not payload_raw:
        raise HTTPException(status_code=400, detail="Payload ausente.")
    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Payload inválido.") from exc

    actions = payload.get("actions") or []
    if not actions:
        return {"ok": True}

    action = actions[0]
    action_id = action.get("action_id")
    draft_id = action.get("value")
    revisor = (payload.get("user") or {}).get("username") or "slack"

    try:
        if action_id == "draft_aprobar":
            hitl.aprobar(draft_id, revisor=revisor, comentario="Aprobado desde Slack")
            return {"text": f":white_check_mark: Borrador {draft_id} aprobado por {revisor}."}
        if action_id == "draft_rechazar":
            hitl.rechazar(draft_id, revisor=revisor, comentario="Rechazado desde Slack")
            return {"text": f":x: Borrador {draft_id} rechazado por {revisor}."}
    except KeyError:
        return {"text": f":warning: Borrador {draft_id} no encontrado."}
    except TransicionInvalida as exc:
        return {"text": f":warning: {exc}"}

    return {"ok": True}
