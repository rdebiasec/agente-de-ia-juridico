"""APIs front-office cliente + inbox abogado + transcript (Fases 1/3/5 local)."""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from src.auth.cliente_session import (
    CLIENTE_COOKIE_NAME,
    cliente_subject_from_token,
    create_cliente_session_token,
)
from src.auth.deps import cookie_secure, require_web_session
from src.auth.gate import COOKIE_NAME as LAWYER_COOKIE_NAME
from src.config import get_settings
from src.services import triple_chat as tc

cliente_router = APIRouter(tags=["cliente-front"])
abogado_router = APIRouter(
    tags=["abogado-cliente"],
    dependencies=[Depends(require_web_session)],
)

_RATE_WINDOW_S = 60.0
_RATE_MAX = 12
_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


def _rate_limit_or_429(key: str) -> None:
    now = time.monotonic()
    bucket = _rate_buckets[key]
    while bucket and now - bucket[0] > _RATE_WINDOW_S:
        bucket.popleft()
    if len(bucket) >= _RATE_MAX:
        raise HTTPException(
            status_code=429,
            detail="Demasiados mensajes. Espere un momento e intente de nuevo.",
        )
    bucket.append(now)


def _apply_cliente_cookie(response: Response, subject: str) -> None:
    settings = get_settings()
    token = create_cliente_session_token(settings.session_secret, subject_id=subject)
    response.set_cookie(
        key=CLIENTE_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=cookie_secure(settings),
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/cliente",
    )


def _resolve_cliente_subject(
    *,
    body_subject: str | None,
    cookie_token: str | None,
) -> str:
    settings = get_settings()
    from_cookie = cliente_subject_from_token(settings.session_secret, cookie_token)
    raw = (from_cookie or body_subject or "").strip()
    if not raw:
        raise tc.TripleChatError("cliente_session_id requerido.")
    return raw


class ClienteChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    cliente_session_id: str | None = Field(
        default=None,
        description="Subject cliente; si hay cookie lexiatek_cliente_session, esta manda.",
    )
    lawyer_session_id: str | None = None
    subject_label: str = ""


class OutboundApproveRequest(BaseModel):
    revisor: str = "abogado"
    comentario: str | None = None
    edited_text: str | None = None


class OutboundEditRequest(BaseModel):
    contenido: str = Field(..., min_length=1)
    revisor: str = "abogado"
    comentario: str | None = None


class OutboundRejectRequest(BaseModel):
    revisor: str = "abogado"
    comentario: str = Field(..., min_length=1)


def _http(exc: tc.TripleChatError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@cliente_router.post("/cliente/chat")
async def cliente_chat(
    req: ClienteChatRequest,
    request: Request,
    response: Response,
    lexiatek_cliente_session: str | None = Cookie(default=None, alias=CLIENTE_COOKIE_NAME),
):
    """Encola propuesta HITL. Cookie cliente ≠ cookie abogado (`agente_session`)."""
    # Defensa: no tomar identidad del desk aunque el navegador envíe ambas cookies.
    _ = request.cookies.get(LAWYER_COOKIE_NAME)
    try:
        subject = _resolve_cliente_subject(
            body_subject=req.cliente_session_id,
            cookie_token=lexiatek_cliente_session,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc

    client_ip = request.client.host if request.client else "unknown"
    _rate_limit_or_429(f"{client_ip}:{subject}")
    try:
        out = tc.enqueue_client_message(
            message=req.message,
            cliente_subject=subject,
            lawyer_session_id=req.lawyer_session_id,
            subject_label=req.subject_label,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc

    # Persistir subject en cookie propia del front-office.
    normalized = out.get("cliente_session_id") or subject
    bare = normalized.split(":", 1)[-1] if normalized.startswith("cliente:") else normalized
    _apply_cliente_cookie(response, bare)
    out["session_cookie"] = CLIENTE_COOKIE_NAME
    return out


@cliente_router.get("/cliente/messages")
async def cliente_messages(
    response: Response,
    cliente_session_id: str | None = None,
    lexiatek_cliente_session: str | None = Cookie(default=None, alias=CLIENTE_COOKIE_NAME),
):
    """Mensajes visibles; identidad por cookie cliente o query."""
    try:
        subject = _resolve_cliente_subject(
            body_subject=cliente_session_id,
            cookie_token=lexiatek_cliente_session,
        )
        data = tc.list_cliente_visible_messages(subject)
    except tc.TripleChatError as exc:
        raise _http(exc) from exc
    bare = subject.split(":", 1)[-1] if subject.startswith("cliente:") else subject
    _apply_cliente_cookie(response, bare)
    return data


@cliente_router.get("/cliente/session")
async def cliente_session_info(
    lexiatek_cliente_session: str | None = Cookie(default=None, alias=CLIENTE_COOKIE_NAME),
):
    """Diagnóstico local: cookie cliente vs cookie abogado (nombres distintos)."""
    settings = get_settings()
    subject = cliente_subject_from_token(settings.session_secret, lexiatek_cliente_session)
    return {
        "cliente_cookie_name": CLIENTE_COOKIE_NAME,
        "lawyer_cookie_name": LAWYER_COOKIE_NAME,
        "cookies_are_separate": CLIENTE_COOKIE_NAME != LAWYER_COOKIE_NAME,
        "cliente_subject": subject,
        "has_cliente_cookie": bool(lexiatek_cliente_session),
    }


@abogado_router.get("/abogado/cliente-inbox")
async def abogado_cliente_inbox(status: str | None = "proposed"):
    try:
        return tc.list_cliente_inbox(status=status)
    except tc.TripleChatError as exc:
        raise _http(exc) from exc


@abogado_router.get("/abogado/cliente-drafts/{draft_id}")
async def abogado_cliente_draft(draft_id: str):
    try:
        return tc.get_outbound_draft(draft_id).to_dict()
    except tc.TripleChatError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@abogado_router.post("/abogado/cliente-drafts/{draft_id}/approve")
async def abogado_approve_draft(draft_id: str, req: OutboundApproveRequest):
    try:
        return tc.approve_outbound_draft(
            draft_id,
            revisor=req.revisor,
            comentario=req.comentario,
            edited_text=req.edited_text,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc


@abogado_router.post("/abogado/cliente-drafts/{draft_id}/edit")
async def abogado_edit_draft(draft_id: str, req: OutboundEditRequest):
    try:
        return tc.edit_outbound_draft(
            draft_id,
            contenido=req.contenido,
            revisor=req.revisor,
            comentario=req.comentario,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc


@abogado_router.post("/abogado/cliente-drafts/{draft_id}/reject")
async def abogado_reject_draft(draft_id: str, req: OutboundRejectRequest):
    try:
        return tc.reject_outbound_draft(
            draft_id,
            revisor=req.revisor,
            comentario=req.comentario,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc


@abogado_router.get("/abogado/internal-transcript")
async def abogado_internal_transcript(session_id: str, limit: int = 100):
    try:
        return tc.list_internal_transcript(session_id, limit=min(max(limit, 1), 500))
    except tc.TripleChatError as exc:
        raise _http(exc) from exc


@abogado_router.post("/abogado/internal-transcript")
async def abogado_append_internal_transcript(
    session_id: str,
    from_actor: str,
    to_actor: str,
    pedido: str = "",
    respuesta: str = "",
    turn_ref: str | None = None,
):
    try:
        entry = tc.append_internal_transcript(
            session_id=session_id,
            from_actor=from_actor,
            to_actor=to_actor,
            pedido=pedido,
            respuesta=respuesta,
            turn_ref=turn_ref,
        )
        return {"ok": True, "entry": entry.to_dict()}
    except tc.TripleChatError as exc:
        raise _http(exc) from exc
