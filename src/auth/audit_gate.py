"""Sesión del portal de auditoría — cookie firmada con correo."""

from __future__ import annotations

import re
import time
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

AUDIT_COOKIE_NAME = "audit_session"
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_audit_email(email: str) -> str:
    return email.strip().lower()


def is_valid_audit_email(email: str) -> bool:
    normalized = normalize_audit_email(email)
    return bool(normalized) and bool(_EMAIL_RE.match(normalized))


def _serializer(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt="audit-portal-v1")


def create_audit_session_token(secret: str, email: str) -> str:
    payload: dict[str, Any] = {
        "last_activity": time.time(),
        "v": 1,
        "email": normalize_audit_email(email),
    }
    return _serializer(secret).dumps(payload)


def parse_audit_session_token(
    secret: str,
    token: str,
    *,
    absolute_max_age: int = 86400,
) -> dict[str, Any] | None:
    try:
        return _serializer(secret).loads(token, max_age=absolute_max_age)
    except (BadSignature, SignatureExpired):
        return None


def is_audit_session_active(
    secret: str,
    token: str | None,
    *,
    idle_seconds: int,
    absolute_max_age: int = 86400,
) -> bool:
    if not token:
        return False
    data = parse_audit_session_token(secret, token, absolute_max_age=absolute_max_age)
    if not data:
        return False
    last_activity = float(data.get("last_activity", 0))
    return (time.time() - last_activity) <= idle_seconds


def refresh_audit_session_token(
    secret: str,
    token: str | None,
    *,
    idle_seconds: int,
    absolute_max_age: int = 86400,
) -> str | None:
    if not is_audit_session_active(
        secret, token, idle_seconds=idle_seconds, absolute_max_age=absolute_max_age
    ):
        return None
    data = parse_audit_session_token(secret, token, absolute_max_age=absolute_max_age)
    email = str((data or {}).get("email", "")).strip()
    if not email:
        return None
    return create_audit_session_token(secret, email)


def audit_email_from_token(
    secret: str,
    token: str | None,
    *,
    idle_seconds: int,
    absolute_max_age: int = 86400,
) -> str | None:
    if not is_audit_session_active(
        secret, token, idle_seconds=idle_seconds, absolute_max_age=absolute_max_age
    ):
        return None
    data = parse_audit_session_token(secret, token, absolute_max_age=absolute_max_age)
    if not data:
        return None
    email = normalize_audit_email(str(data.get("email", "")))
    return email or None
