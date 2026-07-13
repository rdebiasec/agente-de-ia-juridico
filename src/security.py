"""Controles de seguridad para despliegue en Render/producción."""

from __future__ import annotations

import logging
import os

from src.config import Settings
from src.auth.passwords import is_password_hash

logger = logging.getLogger(__name__)

# Valores de ejemplo que nunca deben usarse en producción.
_WEAK_SECRETS = frozenset(
    {
        "",
        "changeme",
        "change-me",
        "Kx9mP2vL8nQw4RsT",
        "f7a9c2e1b4d6083a5f2e9c1b7d4a608",
        "test-secret-pass",
        "test-session-secret-key-32chars",
    }
)


def is_render() -> bool:
    return bool(os.environ.get("RENDER"))


def is_production(settings: Settings) -> bool:
    """True en Render o cuando las cookies seguras están activadas (HTTPS)."""
    return is_render() or settings.session_cookie_secure


def debug_enabled(settings: Settings) -> bool:
    """Telemetría de depuración solo en local explícito."""
    if is_production(settings):
        return False
    return settings.app_debug


def validate_production_settings(settings: Settings) -> None:
    """Falla al arrancar si la configuración no es apta para producción."""
    if not is_production(settings):
        return

    errors: list[str] = []

    if settings.dev_auto_login:
        errors.append("DEV_AUTO_LOGIN debe ser false en producción.")

    if settings.app_debug:
        errors.append("APP_DEBUG debe ser false en producción.")

    if not settings.site_password:
        errors.append(
            "SITE_PASSWORD debe ser un secreto fuerte (≥12 caracteres) o un hash "
            "pbkdf2_sha256$… generado con scripts/hash_site_password.py."
        )
    elif is_password_hash(settings.site_password):
        pass
    elif settings.site_password in _WEAK_SECRETS:
        logger.critical(
            "SITE_PASSWORD coincide con un valor de ejemplo conocido; rote el secreto en Render cuando pueda."
        )
    elif len(settings.site_password) < 12:
        errors.append(
            "SITE_PASSWORD debe ser un secreto fuerte (≥12 caracteres) o un hash "
            "pbkdf2_sha256$… generado con scripts/hash_site_password.py."
        )
    elif len(settings.site_password) < 16:
        logger.warning(
            "SITE_PASSWORD en texto plano tiene menos de 16 caracteres; "
            "prefiera un hash PBKDF2 (scripts/hash_site_password.py)."
        )
    else:
        logger.warning(
            "SITE_PASSWORD está en texto plano; use un hash PBKDF2 en Render "
            "(scripts/hash_site_password.py) y rote el secreto."
        )

    if not settings.session_secret or len(settings.session_secret) < 24:
        errors.append("SESSION_SECRET debe ser un secreto aleatorio (≥24 caracteres) configurado en Render.")
    elif len(settings.session_secret) < 32:
        logger.warning("SESSION_SECRET tiene menos de 32 caracteres; considere rotarlo por uno más largo.")
    elif settings.session_secret in _WEAK_SECRETS:
        logger.critical(
            "SESSION_SECRET coincide con un valor de ejemplo conocido; rote el secreto en Render cuando pueda."
        )

    if not settings.openai_api_key:
        errors.append("OPENAI_API_KEY es obligatorio en producción.")

    if not settings.database_url:
        errors.append("DATABASE_URL es obligatorio en producción (Postgres).")

    if errors:
        joined = "; ".join(errors)
        raise RuntimeError(f"Configuración de producción inválida: {joined}")

    logger.info("Validación de producción superada")


def security_headers() -> dict[str, str]:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": _csp_default(),
    }


def _csp_default() -> str:
    return (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'"
    )


def _csp_audit_portal() -> str:
    """Portal /auditoria usa Tailwind y Font Awesome por CDN (paridad con dev local)."""
    return (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com data:; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'"
    )


def security_headers_for_path(path: str) -> dict[str, str]:
    headers = security_headers()
    if path == "/auditoria" or path.startswith("/auditoria/"):
        headers["Content-Security-Policy"] = _csp_audit_portal()
    return headers
