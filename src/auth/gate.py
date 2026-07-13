"""Acceso web por contraseña — cookie firmada con expiración por inactividad."""

from __future__ import annotations

import secrets
import time
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.auth.passwords import hash_password, is_password_hash, verify_password

COOKIE_NAME = "agente_session"

__all__ = [
    "COOKIE_NAME",
    "auth_enabled",
    "create_session_token",
    "hash_password",
    "is_password_hash",
    "is_session_active",
    "new_subject_id",
    "parse_session_token",
    "refresh_session_token",
    "subject_id_from_token",
    "verify_password",
]


def _serializer(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt="agente-web-gate-v1")


def new_subject_id() -> str:
    """Identificador estable del despacho en este navegador (SEC-01)."""
    return f"web-{secrets.token_hex(4)}"


def create_session_token(
    secret: str,
    username: str | None = None,
    *,
    subject_id: str | None = None,
) -> str:
    payload: dict[str, Any] = {
        "last_activity": time.time(),
        "v": 2,
        "subject_id": subject_id or new_subject_id(),
    }
    if username:
        payload["username"] = username
    return _serializer(secret).dumps(payload)


def parse_session_token(secret: str, token: str, *, absolute_max_age: int = 86400) -> dict[str, Any] | None:
    try:
        return _serializer(secret).loads(token, max_age=absolute_max_age)
    except (BadSignature, SignatureExpired):
        return None


def subject_id_from_token(secret: str, token: str | None, *, absolute_max_age: int = 86400) -> str | None:
    if not token:
        return None
    data = parse_session_token(secret, token, absolute_max_age=absolute_max_age)
    if not data:
        return None
    sid = str(data.get("subject_id") or "").strip()
    return sid or None


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
    if not data:
        return None
    username = str(data.get("username", "")) if data else None
    subject_id = str(data.get("subject_id") or "").strip() or new_subject_id()
    return create_session_token(secret, username=username or None, subject_id=subject_id)


def auth_enabled(site_password: str) -> bool:
    return bool(site_password.strip())
