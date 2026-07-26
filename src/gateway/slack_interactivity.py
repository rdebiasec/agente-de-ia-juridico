"""Webhook HTTP de interactividad Slack + lógica compartida con Bolt Socket Mode.

Verifica la firma con `SLACK_SIGNING_SECRET` (docs.slack.dev verifying-requests-from-slack).
Botones en `src/hitl/slack_review.py` (`draft_aprobar` / `draft_editar` / `draft_rechazar`).

Con Socket Mode activado, Slack envía interacciones por WebSocket (handlers en
`src/channels/slack_bot.py`). Este endpoint queda como respaldo si Socket Mode está off.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.hitl import drafts as hitl
from src.hitl.drafts import TransicionInvalida
from src.hitl.slack_review import (
    DRAFT_COMMENT_ACTION,
    DRAFT_CONTENT_ACTION,
    DRAFT_EDIT_CALLBACK,
    actualizar_mensaje_resultado,
    build_edit_modal,
)
from src.storage import get_repository

logger = logging.getLogger(__name__)

router = APIRouter()


class SlackAuthError(PermissionError):
    """El usuario de Slack no está autorizado a revisar borradores."""


def format_slack_revisor(user: dict[str, Any] | None) -> str:
    """Identidad auditable: prioriza Slack user.id."""
    data = user or {}
    user_id = str(data.get("id") or "").strip()
    username = str(data.get("username") or data.get("name") or "").strip()
    if user_id and username:
        return f"{user_id}|{username}"
    return user_id or username or "slack"


def ensure_slack_approver(user: dict[str, Any] | None) -> str:
    """Valida allowlist (si está configurada) y devuelve el revisor formateado."""
    settings = get_settings()
    allow = settings.slack_approver_allowlist()
    data = user or {}
    user_id = str(data.get("id") or "").strip()
    if allow and user_id not in allow:
        raise SlackAuthError(
            "No está autorizado para aprobar o editar borradores jurídicos en Slack."
        )
    return format_slack_revisor(data)


def aplicar_accion_borrador(
    action_id: str | None,
    draft_id: str | None,
    revisor: str = "slack",
    *,
    channel: str | None = None,
    message_ts: str | None = None,
) -> str | None:
    """Aplica aprobar/rechazar. Devuelve texto de respuesta Slack o None si no aplica."""
    if not action_id or not draft_id:
        return None
    try:
        if action_id == "draft_aprobar":
            draft = hitl.aprobar(
                draft_id, revisor=revisor, comentario="Aprobado desde Slack"
            )
            actualizar_mensaje_resultado(
                draft,
                channel=channel,
                message_ts=message_ts or draft.slack_ts,
                estado_label=":white_check_mark: Aprobado",
            )
            return f":white_check_mark: Borrador {draft_id} aprobado por {revisor}."
        if action_id == "draft_rechazar":
            draft = hitl.rechazar(
                draft_id, revisor=revisor, comentario="Rechazado desde Slack"
            )
            actualizar_mensaje_resultado(
                draft,
                channel=channel,
                message_ts=message_ts or draft.slack_ts,
                estado_label=":x: Rechazado",
            )
            return f":x: Borrador {draft_id} rechazado por {revisor}."
    except KeyError:
        return f":warning: Borrador {draft_id} no encontrado."
    except TransicionInvalida as exc:
        return f":warning: {exc}"
    return None


def aplicar_edicion_borrador(
    draft_id: str,
    *,
    revisor: str,
    nuevo_contenido: str,
    comentario: str | None = None,
    channel: str | None = None,
    message_ts: str | None = None,
) -> str:
    draft = hitl.editar(
        draft_id,
        revisor=revisor,
        nuevo_contenido=nuevo_contenido,
        comentario=comentario or "Editado desde Slack",
    )
    actualizar_mensaje_resultado(
        draft,
        channel=channel,
        message_ts=message_ts or draft.slack_ts,
        estado_label=":pencil2: Editado y aprobado",
    )
    return f":pencil2: Borrador {draft_id} editado por {revisor}."


def _extract_modal_values(view: dict[str, Any]) -> tuple[str, str | None]:
    values = (view.get("state") or {}).get("values") or {}
    contenido = (
        ((values.get("contenido_block") or {}).get(DRAFT_CONTENT_ACTION) or {}).get(
            "value"
        )
        or ""
    ).strip()
    comentario_raw = (
        ((values.get("comentario_block") or {}).get(DRAFT_COMMENT_ACTION) or {}).get(
            "value"
        )
        or ""
    ).strip()
    return contenido, (comentario_raw or None)


def _verificar_firma(body: bytes, timestamp: str | None, signature: str | None, secret: str) -> bool:
    try:
        from slack_sdk.signature import SignatureVerifier

        verifier = SignatureVerifier(signing_secret=secret)
        return verifier.is_valid(body=body, timestamp=timestamp or "", signature=signature or "")
    except Exception:  # pragma: no cover - dependencias/entorno
        logger.exception("Fallo al verificar firma de Slack")
        return False


def _open_edit_modal(*, trigger_id: str, draft_id: str) -> str | None:
    draft = get_repository().get_draft(draft_id)
    if draft is None:
        return f":warning: Borrador {draft_id} no encontrado."
    settings = get_settings()
    if not settings.slack_bot_token:
        return ":warning: Slack no está configurado para abrir el modal de edición."
    try:
        from slack_sdk import WebClient

        client = WebClient(token=settings.slack_bot_token)
        client.views_open(trigger_id=trigger_id, view=build_edit_modal(draft))
        return None
    except Exception as exc:  # pragma: no cover
        logger.warning("No se pudo abrir modal de edición: %s", exc)
        return f":warning: No pude abrir el editor: {exc}"


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

    payload_type = payload.get("type")
    user = payload.get("user") or {}
    try:
        revisor = ensure_slack_approver(user)
    except SlackAuthError as exc:
        return {"text": f":no_entry: {exc}"}

    if payload_type == "view_submission":
        view = payload.get("view") or {}
        if view.get("callback_id") != DRAFT_EDIT_CALLBACK:
            return {"ok": True}
        draft_id = str(view.get("private_metadata") or "").strip()
        contenido, comentario = _extract_modal_values(view)
        if not draft_id or not contenido:
            return JSONResponse(
                {
                    "response_action": "errors",
                    "errors": {"contenido_block": "El contenido no puede estar vacío."},
                }
            )
        try:
            texto = aplicar_edicion_borrador(
                draft_id,
                revisor=revisor,
                nuevo_contenido=contenido,
                comentario=comentario,
            )
        except KeyError:
            return JSONResponse(
                {
                    "response_action": "errors",
                    "errors": {"contenido_block": "Borrador no encontrado."},
                }
            )
        except TransicionInvalida as exc:
            return JSONResponse(
                {
                    "response_action": "errors",
                    "errors": {"contenido_block": str(exc)},
                }
            )
        return {"response_action": "clear"}

    actions = payload.get("actions") or []
    if not actions:
        return {"ok": True}

    action = actions[0]
    action_id = action.get("action_id")
    draft_id = action.get("value")
    channel = (payload.get("channel") or {}).get("id")
    message_ts = (payload.get("message") or {}).get("ts")

    if action_id == "draft_editar":
        trigger_id = payload.get("trigger_id")
        if not trigger_id or not draft_id:
            return {"text": ":warning: No pude abrir el editor."}
        err = _open_edit_modal(trigger_id=trigger_id, draft_id=draft_id)
        if err:
            return {"text": err}
        return {"ok": True}

    texto = aplicar_accion_borrador(
        action_id=action_id,
        draft_id=draft_id,
        revisor=revisor,
        channel=channel,
        message_ts=message_ts,
    )
    if texto:
        return {"text": texto}
    return {"ok": True}
