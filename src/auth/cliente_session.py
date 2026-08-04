"""Sesión del front-office víctima — cookie distinta del desk abogado (Fase 5 local)."""

from __future__ import annotations

import secrets
import time
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

# Nunca reutilizar `agente_session` del escritorio.
CLIENTE_COOKIE_NAME = "lexiatek_cliente_session"
_SALT = "lexiatek-cliente-gate-v1"


def _serializer(secret: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret, salt=_SALT)


def new_cliente_subject_id() -> str:
    return f"c-{secrets.token_hex(6)}"


def create_cliente_session_token(
    secret: str,
    *,
    subject_id: str | None = None,
) -> str:
    payload: dict[str, Any] = {
        "v": 1,
        "kind": "cliente",
        "subject_id": subject_id or new_cliente_subject_id(),
        "issued_at": time.time(),
    }
    return _serializer(secret).dumps(payload)


def parse_cliente_session_token(
    secret: str,
    token: str | None,
    *,
    absolute_max_age: int = 60 * 60 * 24 * 30,
) -> dict[str, Any] | None:
    if not token:
        return None
    try:
        data = _serializer(secret).loads(token, max_age=absolute_max_age)
    except (BadSignature, SignatureExpired):
        return None
    if str(data.get("kind") or "") != "cliente":
        return None
    return data


def cliente_subject_from_token(
    secret: str,
    token: str | None,
    *,
    absolute_max_age: int = 60 * 60 * 24 * 30,
) -> str | None:
    data = parse_cliente_session_token(
        secret, token, absolute_max_age=absolute_max_age
    )
    if not data:
        return None
    sid = str(data.get("subject_id") or "").strip()
    return sid or None
