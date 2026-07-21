"""Cifrado en reposo de textos sensibles (borradores y mensajes de chat).

Si no hay clave (`DATA_AT_REST_KEY` ni `SESSION_SECRET`), se almacena en claro
(útil en tests). Con clave, el valor se guarda con prefijo `enc:v1:`.
"""

from __future__ import annotations

import base64
import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

_PREFIX = "enc:v1:"


def _fernet():
    from src.config import get_settings

    settings = get_settings()
    raw = (settings.data_at_rest_key or settings.session_secret or "").strip()
    if not raw:
        return None
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logger.warning("cryptography no instalado; cifrado en reposo desactivado")
        return None
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_text(value: str | None) -> str:
    text = value or ""
    if not text or text.startswith(_PREFIX):
        return text
    f = _fernet()
    if f is None:
        return text
    token = f.encrypt(text.encode("utf-8")).decode("ascii")
    return f"{_PREFIX}{token}"


def decrypt_text(value: str | None) -> str:
    text = value or ""
    if not text.startswith(_PREFIX):
        return text
    f = _fernet()
    if f is None:
        logger.warning("Texto cifrado sin clave disponible; se devuelve vacío")
        return ""
    token = text[len(_PREFIX) :].encode("ascii")
    try:
        from cryptography.fernet import InvalidToken

        return f.decrypt(token).decode("utf-8")
    except InvalidToken:
        logger.exception("No se pudo descifrar texto en reposo")
        return ""
    except Exception:
        logger.exception("Error descifrando texto en reposo")
        return ""


def encrypt_messages(messages: list[dict] | None) -> list[dict]:
    out: list[dict] = []
    for msg in messages or []:
        item = dict(msg)
        if isinstance(item.get("content"), str):
            item["content"] = encrypt_text(item["content"])
        out.append(item)
    return out


def decrypt_messages(messages: list[dict] | None) -> list[dict]:
    out: list[dict] = []
    for msg in messages or []:
        item = dict(msg)
        if isinstance(item.get("content"), str):
            item["content"] = decrypt_text(item["content"])
        out.append(item)
    return out


def encryption_enabled() -> bool:
    return _fernet() is not None


def status_payload() -> dict[str, Any]:
    return {
        "at_rest_encryption": encryption_enabled(),
        "prefix": _PREFIX if encryption_enabled() else None,
    }
