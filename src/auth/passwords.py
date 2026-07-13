"""Hash y verificación de contraseña del sitio (PBKDF2-SHA256, sin deps extra).

`SITE_PASSWORD` acepta:
- texto plano (compatibilidad local / migración); o
- hash `pbkdf2_sha256$<iters>$<salt_hex>$<digest_hex>` (recomendado en prod).
"""

from __future__ import annotations

import hashlib
import secrets

PASSWORD_PREFIX = "pbkdf2_sha256$"
DEFAULT_ITERATIONS = 210_000


def is_password_hash(stored: str) -> bool:
    return stored.startswith(PASSWORD_PREFIX) and stored.count("$") >= 3


def hash_password(plain: str, *, iterations: int = DEFAULT_ITERATIONS) -> str:
    if not plain:
        raise ValueError("La contraseña no puede estar vacía.")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain.encode("utf-8"),
        bytes.fromhex(salt),
        iterations,
    )
    return f"{PASSWORD_PREFIX}{iterations}${salt}${digest.hex()}"


def verify_password(stored: str, provided: str) -> bool:
    """Verifica contra hash PBKDF2 o texto plano legado."""
    if not stored:
        return False
    if is_password_hash(stored):
        try:
            _, iters_s, salt_hex, expected_hex = stored.split("$", 3)
            iterations = int(iters_s)
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                provided.encode("utf-8"),
                bytes.fromhex(salt_hex),
                iterations,
            )
            return secrets.compare_digest(digest.hex(), expected_hex)
        except (ValueError, TypeError):
            return False
    return secrets.compare_digest(stored, provided)
