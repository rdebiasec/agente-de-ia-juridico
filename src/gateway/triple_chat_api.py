"""APIs front-office cliente + inbox abogado + canal víctima + transcript."""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import APIRouter, Cookie, Depends, File, Form, HTTPException, Request, Response, UploadFile
from pydantic import BaseModel, Field

from src.auth.cliente_session import (
    CLIENTE_COOKIE_NAME,
    cliente_subject_from_token,
    create_cliente_session_token,
    new_cliente_subject_id,
)
from src.auth.deps import cookie_secure, require_web_session, resolve_web_user_id
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
_RATE_IMPERSONATION_MAX = 8
_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


def _rate_limit_or_429(key: str, *, max_hits: int = _RATE_MAX) -> None:
    now = time.monotonic()
    bucket = _rate_buckets[key]
    while bucket and now - bucket[0] > _RATE_WINDOW_S:
        bucket.popleft()
    if len(bucket) >= max_hits:
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
        path="/",
    )


def _resolve_cliente_subject(
    *,
    body_subject: str | None,
    cookie_token: str | None,
    allow_create: bool = False,
) -> str:
    settings = get_settings()
    from_cookie = cliente_subject_from_token(settings.session_secret, cookie_token)
    raw = (from_cookie or body_subject or "").strip()
    if not raw:
        if allow_create:
            return new_cliente_subject_id()
        raise tc.TripleChatError("cliente_session_id requerido.")
    return raw


class ClienteStartRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    telefono: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=120)
    consent_1581: bool = False
    lawyer_session_id: str | None = None
    cliente_session_id: str | None = None


class ClienteChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    cliente_session_id: str | None = Field(
        default=None,
        description="Subject cliente; si hay cookie lexiatek_cliente_session, esta manda.",
    )
    lawyer_session_id: str | None = None
    subject_label: str = ""


class LawyerAsClientRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    session_id: str = Field(..., min_length=3, max_length=120)


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


@cliente_router.post("/cliente/start")
async def cliente_start(
    req: ClienteStartRequest,
    request: Request,
    response: Response,
    lexiatek_cliente_session: str | None = Cookie(default=None, alias=CLIENTE_COOKIE_NAME),
):
    """Inicio webchat: nombre + consentimiento 1581 (servidor) + cookie subject."""
    _ = request.cookies.get(LAWYER_COOKIE_NAME)
    try:
        subject = _resolve_cliente_subject(
            body_subject=req.cliente_session_id,
            cookie_token=lexiatek_cliente_session,
            allow_create=True,
        )
        out = tc.start_cliente_session(
            nombre=req.nombre,
            consent_1581=req.consent_1581,
            cliente_subject=subject,
            lawyer_session_id=req.lawyer_session_id,
            telefono=req.telefono,
            email=req.email,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc

    normalized = out.get("cliente_session_id") or subject
    bare = normalized.split(":", 1)[-1] if normalized.startswith("cliente:") else normalized
    _apply_cliente_cookie(response, bare)
    out["session_cookie"] = CLIENTE_COOKIE_NAME
    return out


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


@cliente_router.post("/cliente/upload")
async def cliente_upload(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    lawyer_session_id: str | None = Form(default=None),
    cliente_session_id: str | None = Form(default=None),
    lexiatek_cliente_session: str | None = Cookie(default=None, alias=CLIENTE_COOKIE_NAME),
):
    """Adjunto de la víctima → expediente del abogado + mensaje en el hilo."""
    _ = request.cookies.get(LAWYER_COOKIE_NAME)
    try:
        subject = _resolve_cliente_subject(
            body_subject=cliente_session_id,
            cookie_token=lexiatek_cliente_session,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc

    client_ip = request.client.host if request.client else "unknown"
    _rate_limit_or_429(f"upload:{client_ip}:{subject}", max_hits=8)

    try:
        out = tc.register_cliente_upload(
            cliente_subject=subject,
            lawyer_session_id=lawyer_session_id,
            filename=file.filename or "archivo",
            data=await file.read(),
            content_type=file.content_type,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc

    bare = subject.split(":", 1)[-1] if subject.startswith("cliente:") else subject
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
    """Estado de identidad consumidor (cookie + consentimiento)."""
    settings = get_settings()
    subject = cliente_subject_from_token(settings.session_secret, lexiatek_cliente_session)
    started = False
    display_name = None
    consent_at = None
    if subject:
        try:
            data = tc.list_cliente_visible_messages(subject)
            started = bool(data.get("started"))
            display_name = data.get("client_display_name")
            consent_at = data.get("consent_at")
        except tc.TripleChatError:
            pass
    return {
        "cliente_cookie_name": CLIENTE_COOKIE_NAME,
        "lawyer_cookie_name": LAWYER_COOKIE_NAME,
        "cookies_are_separate": CLIENTE_COOKIE_NAME != LAWYER_COOKIE_NAME,
        "cliente_subject": subject,
        "has_cliente_cookie": bool(lexiatek_cliente_session),
        "started": started,
        "client_display_name": display_name,
        "consent_at": consent_at,
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


@abogado_router.get("/abogado/cliente-thread")
async def abogado_cliente_thread(session_id: str):
    """Hilo canal víctima del caso (desk)."""
    try:
        return tc.list_lawyer_cliente_thread(session_id)
    except tc.TripleChatError as exc:
        raise _http(exc) from exc


@abogado_router.get("/abogado/cliente-attachments/{attachment_id}")
async def abogado_cliente_attachment(attachment_id: str, session_id: str):
    """Descarga un adjunto subido por la víctima (solo desk)."""
    from fastapi.responses import FileResponse

    from src.services.cliente_uploads import find_attachment, resolve_attachment_path

    lawyer_sid = tc.normalize_lawyer_session(session_id)
    meta = find_attachment(lawyer_session_id=lawyer_sid, attachment_id=attachment_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado.")
    path = resolve_attachment_path(str(meta.get("rel_path") or ""))
    if not path:
        raise HTTPException(status_code=404, detail="Archivo no disponible.")
    return FileResponse(
        path,
        filename=str(meta.get("filename") or path.name),
        media_type=str(meta.get("content_type") or "application/octet-stream"),
    )


@abogado_router.post("/abogado/cliente-as-client")
async def abogado_cliente_as_client(
    req: LawyerAsClientRequest,
    request: Request,
    response: Response,
    agente_session: str | None = Cookie(default=None),
):
    """Escribir como la víctima en el mismo hilo; sigue creando borrador HITL."""
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    _rate_limit_or_429(
        f"impersonate:{client_ip}:{req.session_id}",
        max_hits=_RATE_IMPERSONATION_MAX,
    )
    try:
        actor = resolve_web_user_id(
            settings,
            agente_session,
            client_fallback=request.query_params.get("user_id"),
            response=response,
        )
        out = tc.enqueue_lawyer_as_client(
            message=req.text,
            lawyer_session_id=req.session_id,
            lawyer_actor_id=actor,
        )
    except tc.TripleChatError as exc:
        raise _http(exc) from exc
    except HTTPException:
        raise
    return out


@abogado_router.get("/abogado/internal-transcript")
async def abogado_internal_transcript(session_id: str, limit: int = 100):
    try:
        return tc.list_internal_transcript(session_id, limit=min(max(limit, 1), 500))
    except tc.TripleChatError as exc:
        raise _http(exc) from exc


@abogado_router.get("/abogado/attribution-entry")
async def abogado_attribution_entry(
    session_id: str,
    hint: str = "",
    turn_ref: str | None = None,
):
    """Punto de anclaje para «¿De dónde salió esto?» → Junta del caso (nunca cliente)."""
    from src.services.attribution import find_attribution_entry
    from src.services.triple_chat import _actor_label

    try:
        # Valida session_id con el mismo contrato del transcript.
        tc.list_internal_transcript(session_id, limit=1)
    except tc.TripleChatError as exc:
        raise _http(exc) from exc
    entry = find_attribution_entry(session_id, hint=hint, turn_ref=turn_ref)
    if entry is None:
        return {"ok": True, "entry": None}
    data = entry.to_dict()
    data["from_label"] = _actor_label(entry.from_actor, short=True)
    data["to_label"] = _actor_label(entry.to_actor, short=True)
    return {"ok": True, "entry": data}


@abogado_router.post("/abogado/internal-transcript")
async def abogado_append_internal_transcript(
    session_id: str,
    from_actor: str,
    to_actor: str,
    pedido: str = "",
    respuesta: str = "",
    turn_ref: str | None = None,
    kind: str | None = None,
    ronda: int | None = None,
):
    try:
        entry = tc.append_internal_transcript(
            session_id=session_id,
            from_actor=from_actor,
            to_actor=to_actor,
            pedido=pedido,
            respuesta=respuesta,
            turn_ref=turn_ref,
            kind=kind,
            ronda=ronda,
        )
        return {"ok": True, "entry": entry.to_dict()}
    except tc.TripleChatError as exc:
        raise _http(exc) from exc
