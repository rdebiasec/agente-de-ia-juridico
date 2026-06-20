"""Acceso web por contraseña — cookie firmada con expiración por inactividad."""

from __future__ import annotations

import secrets
import time
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

COOKIE_NAME = "agente_session"


def _serializer(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt="agente-web-gate-v1")


def create_session_token(secret: str, username: str | None = None) -> str:
    payload: dict[str, Any] = {"last_activity": time.time(), "v": 1}
    if username:
        payload["username"] = username
    return _serializer(secret).dumps(payload)


def parse_session_token(secret: str, token: str, *, absolute_max_age: int = 86400) -> dict[str, Any] | None:
    try:
        return _serializer(secret).loads(token, max_age=absolute_max_age)
    except (BadSignature, SignatureExpired):
        return None


def is_session_active(
    secret: str,
    token: str | None,
    *,
    idle_seconds: int,
    absolute_max_age: int = 86400,
) -> bool:
    if not token:
        return False
    data = parse_session_token(secret, token, absolute_max_age=absolute_max_age)
    if not data:
        return False
    last_activity = float(data.get("last_activity", 0))
    return (time.time() - last_activity) <= idle_seconds


def refresh_session_token(
    secret: str,
    token: str | None,
    *,
    idle_seconds: int,
    absolute_max_age: int = 86400,
) -> str | None:
    if not is_session_active(secret, token, idle_seconds=idle_seconds, absolute_max_age=absolute_max_age):
        return None
    data = parse_session_token(secret, token, absolute_max_age=absolute_max_age)
    username = str(data.get("username", "")) if data else None
    return create_session_token(secret, username=username or None)


def verify_password(expected: str, provided: str) -> bool:
    if not expected:
        return False
    return secrets.compare_digest(expected, provided)


def auth_enabled(site_password: str) -> bool:
    return bool(site_password.strip())
