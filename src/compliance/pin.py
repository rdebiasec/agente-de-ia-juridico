"""PIN personal del portal de auditoría (hash PBKDF2, sin dependencias extra)."""

from __future__ import annotations

import hashlib
import secrets


def _normalize_pin(pin: str) -> str:
    return "".join(ch for ch in pin.strip() if ch.isdigit())


def validate_pin_format(pin: str) -> bool:
    digits = _normalize_pin(pin)
    return 6 <= len(digits) <= 8


def hash_pin(pin: str) -> str:
    digits = _normalize_pin(pin)
    if not validate_pin_format(digits):
        raise ValueError("PIN inválido: use 6 a 8 dígitos.")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", digits.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"{salt}${digest.hex()}"


def verify_pin(pin: str, stored: str) -> bool:
    digits = _normalize_pin(pin)
    if not validate_pin_format(digits) or "$" not in stored:
        return False
    salt, expected_hex = stored.split("$", 1)
    digest = hashlib.pbkdf2_hmac("sha256", digits.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return secrets.compare_digest(digest.hex(), expected_hex)
