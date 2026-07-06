"""API del portal de auditoría — login por correo y persistencia en Postgres."""

from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from src.auth.audit_gate import (
    AUDIT_COOKIE_NAME,
    audit_email_from_token,
    create_audit_session_token,
    is_valid_audit_email,
    normalize_audit_email,
    refresh_audit_session_token,
)
from src.auth.deps import cookie_secure, idle_seconds
from src.auth.gate import auth_enabled, verify_password
from src.config import Settings, get_settings
from src.storage import get_repository

router = APIRouter(prefix="/api/audit", tags=["audit-portal"])


class AuditLoginBody(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1)


class AuditProgressBody(BaseModel):
    version: int | None = None
    savedAt: str | None = None
    catalogGeneratedAt: str | None = None
    guardrails: dict = Field(default_factory=dict)
    agentes: dict = Field(default_factory=dict)
    pasos: dict = Field(default_factory=dict)
    custom: dict | None = None


def _apply_audit_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=AUDIT_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=cookie_secure(settings),
        samesite="none" if cookie_secure(settings) else "lax",
        max_age=idle_seconds(settings),
        path="/",
    )


def _clear_audit_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=AUDIT_COOKIE_NAME,
        path="/",
        secure=cookie_secure(settings),
        httponly=True,
        samesite="none" if cookie_secure(settings) else "lax",
    )


def _require_audit_email(
    request: Request,
    response: Response,
    audit_session: str | None = Cookie(default=None),
    settings: Settings = Depends(get_settings),
) -> str:
    if not auth_enabled(settings.site_password):
        raise HTTPException(
            status_code=503,
            detail="Auditoría no disponible: configure SITE_PASSWORD en el servidor.",
        )
    refreshed = refresh_audit_session_token(
        settings.session_secret,
        audit_session,
        idle_seconds=idle_seconds(settings),
    )
    if not refreshed:
        raise HTTPException(status_code=401, detail="Sesión de auditoría expirada o no autenticada.")
    _apply_audit_cookie(response, refreshed, settings)
    email = audit_email_from_token(
        settings.session_secret,
        refreshed,
        idle_seconds=idle_seconds(settings),
    )
    if not email:
        raise HTTPException(status_code=401, detail="Sesión de auditoría inválida.")
    request.state.audit_email = email
    return email


@router.post("/login")
async def audit_login(
    body: AuditLoginBody,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    if not auth_enabled(settings.site_password):
        raise HTTPException(
            status_code=503,
            detail="Auditoría no disponible: configure SITE_PASSWORD en el servidor.",
        )
    email = normalize_audit_email(body.email)
    if not is_valid_audit_email(email):
        raise HTTPException(status_code=400, detail="Correo electrónico inválido.")
    if not verify_password(settings.site_password, body.password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

    token = create_audit_session_token(settings.session_secret, email)
    _apply_audit_cookie(response, token, settings)
    return {"ok": True, "authenticated": True, "email": email}


@router.get("/session")
async def audit_session(
    request: Request,
    response: Response,
    audit_session: str | None = Cookie(default=None),
    settings: Settings = Depends(get_settings),
):
    if not auth_enabled(settings.site_password):
        return {"authenticated": False, "email": None, "auth_enabled": False}

    refreshed = refresh_audit_session_token(
        settings.session_secret,
        audit_session,
        idle_seconds=idle_seconds(settings),
    )
    if not refreshed:
        return {"authenticated": False, "email": None, "auth_enabled": True}
    _apply_audit_cookie(response, refreshed, settings)
    email = audit_email_from_token(
        settings.session_secret,
        refreshed,
        idle_seconds=idle_seconds(settings),
    )
    return {"authenticated": bool(email), "email": email, "auth_enabled": True}


@router.post("/logout")
async def audit_logout(
    response: Response,
    settings: Settings = Depends(get_settings),
):
    _clear_audit_cookie(response, settings)
    return {"ok": True}


@router.get("/progress")
async def get_audit_progress(email: str = Depends(_require_audit_email)):
    repo = get_repository()
    row = repo.get_audit_portal_progress(email)
    if row is None:
        raise HTTPException(status_code=404, detail="Sin progreso guardado para este correo.")
    return row.payload


@router.put("/progress")
async def put_audit_progress(
    body: AuditProgressBody,
    email: str = Depends(_require_audit_email),
):
    repo = get_repository()
    payload = body.model_dump()
    row = repo.save_audit_portal_progress(email, payload)
    return {
        "ok": True,
        "email": row.email,
        "updated_at": row.updated_at.isoformat(),
    }


@router.delete("/progress")
async def delete_audit_progress(email: str = Depends(_require_audit_email)):
    repo = get_repository()
    deleted = repo.delete_audit_portal_progress(email)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sin progreso guardado para este correo.")
    return {"ok": True, "deleted": True}
