"""Utilidades de conveniencia solo para entorno local de desarrollo."""

from __future__ import annotations

import os
from html import escape

from fastapi import Request, Response
from fastapi.responses import RedirectResponse

from src.auth.deps import apply_session_cookie, idle_seconds
from src.auth.gate import COOKIE_NAME, auth_enabled, create_session_token, is_session_active
from src.config import Settings


def dev_auto_login_allowed(settings: Settings) -> bool:
    """True solo en desarrollo local explícito; nunca en Render ni con cookies seguras."""
    if not settings.dev_auto_login:
        return False
    if os.environ.get("RENDER"):
        return False
    if settings.session_cookie_secure:
        return False
    return True


def web_session_is_active(request: Request, settings: Settings) -> bool:
    token = request.cookies.get(COOKIE_NAME)
    return is_session_active(
        settings.session_secret,
        token,
        idle_seconds=idle_seconds(settings),
    )


def apply_dev_auto_login(response: Response, settings: Settings) -> None:
    token = create_session_token(settings.session_secret, username=settings.site_username)
    apply_session_cookie(response, token, settings)


def dev_auto_login_redirect(request: Request, settings: Settings, *, next_url: str) -> RedirectResponse | None:
    if not auth_enabled(settings.site_password):
        return None
    if not dev_auto_login_allowed(settings):
        return None
    if web_session_is_active(request, settings):
        return None
    redirect = RedirectResponse(url=next_url, status_code=302)
    apply_dev_auto_login(redirect, settings)
    return redirect


def login_html_with_dev_prefill(html: str, settings: Settings) -> str:
    username = escape(settings.site_username, quote=True)
    password = escape(settings.site_password, quote=True)
    html = html.replace(
        'id="auth-username"',
        f'id="auth-username" value="{username}"',
        1,
    )
    html = html.replace(
        'id="auth-password"',
        f'id="auth-password" value="{password}"',
        1,
    )
    return html
