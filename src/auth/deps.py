"""Dependencias FastAPI para proteger rutas web."""

from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, Request, Response

from src.auth.gate import (
    COOKIE_NAME,
    auth_enabled,
    refresh_session_token,
    subject_id_from_token,
)
from src.config import Settings, get_settings


def idle_seconds(settings: Settings) -> int:
    return max(60, settings.session_idle_minutes * 60)


def cookie_secure(settings: Settings) -> bool:
    return settings.session_cookie_secure


def apply_session_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=cookie_secure(settings),
        samesite="lax",
        max_age=idle_seconds(settings),
        path="/",
    )


def clear_session_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        secure=cookie_secure(settings),
        httponly=True,
        samesite="lax",
    )


def resolve_web_user_id(
    settings: Settings,
    token: str | None,
    *,
    client_fallback: str | None = None,
    response: Response | None = None,
) -> str:
    """ID de usuario web: cookie firmada en prod; fallback solo si auth desactivada (tests)."""
    if not auth_enabled(settings.site_password):
        fb = (client_fallback or "test").strip()
        return fb or "test"

    idle = idle_seconds(settings)
    refreshed = refresh_session_token(
        settings.session_secret,
        token,
        idle_seconds=idle,
    )
    if refreshed and response is not None:
        apply_session_cookie(response, refreshed, settings)
        token = refreshed

    subject_id = subject_id_from_token(settings.session_secret, token, absolute_max_age=idle)
    if not subject_id:
        raise HTTPException(status_code=401, detail="Sesión expirada o no autenticada.")
    return subject_id


async def optional_web_session(
    request: Request,
    response: Response,
    agente_session: str | None = Cookie(default=None),
    settings: Settings = Depends(get_settings),
) -> bool:
    if not auth_enabled(settings.site_password):
        return True
    refreshed = refresh_session_token(
        settings.session_secret,
        agente_session,
        idle_seconds=idle_seconds(settings),
    )
    if not refreshed:
        return False
    apply_session_cookie(response, refreshed, settings)
    request.state.web_authenticated = True
    request.state.web_subject_id = subject_id_from_token(
        settings.session_secret,
        refreshed,
        absolute_max_age=idle_seconds(settings),
    )
    return True


async def require_web_session(
    authenticated: bool = Depends(optional_web_session),
    settings: Settings = Depends(get_settings),
) -> None:
    if not auth_enabled(settings.site_password):
        return
    if not authenticated:
        raise HTTPException(status_code=401, detail="Sesión expirada o no autenticada.")


async def get_web_subject_id(
    request: Request,
    response: Response,
    agente_session: str | None = Cookie(default=None),
    settings: Settings = Depends(get_settings),
) -> str:
    """Dependencia para GET sin body — query user_id solo si auth desactivada."""
    client = request.query_params.get("user_id")
    uid = resolve_web_user_id(
        settings,
        agente_session,
        client_fallback=client,
        response=response,
    )
    request.state.web_subject_id = uid
    return uid
