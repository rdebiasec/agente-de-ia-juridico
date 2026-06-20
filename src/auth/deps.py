"""Dependencias FastAPI para proteger rutas web."""

from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, Request, Response

from src.auth.gate import COOKIE_NAME, auth_enabled, refresh_session_token
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
    return True


async def require_web_session(
    authenticated: bool = Depends(optional_web_session),
    settings: Settings = Depends(get_settings),
) -> None:
    if not auth_enabled(settings.site_password):
        return
    if not authenticated:
        raise HTTPException(status_code=401, detail="Sesión expirada o no autenticada.")
