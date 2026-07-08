"""Tests de controles de producción y seguridad."""

from __future__ import annotations

import pytest

from src.config import Settings
from src.security import debug_enabled, is_production, security_headers, validate_production_settings


def test_debug_disabled_in_production(monkeypatch):
    settings = Settings(session_cookie_secure=True, app_debug=True)
    assert is_production(settings) is True
    assert debug_enabled(settings) is False


def test_validate_production_rejects_short_secrets(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    settings = Settings(
        site_password="short",
        session_secret="weak",
        openai_api_key="sk-test",
        database_url="postgresql+psycopg://x",
        session_cookie_secure=True,
    )
    with pytest.raises(RuntimeError, match="SITE_PASSWORD"):
        validate_production_settings(settings)


def test_validate_production_warns_known_weak_but_long_secrets(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    settings = Settings(
        site_password="Kx9mP2vL8nQw4RsT",
        session_secret="f7a9c2e1b4d6083a5f2e9c1b7d4a608",
        openai_api_key="sk-test",
        database_url="postgresql+psycopg://x",
        session_cookie_secure=True,
        dev_auto_login=False,
        app_debug=False,
    )
    logged: list[str] = []

    def _record(msg: str, *args: object) -> None:
        logged.append(msg % args if args else msg)

    monkeypatch.setattr("src.security.logger.critical", _record)
    monkeypatch.setattr("src.security.logger.warning", _record)

    validate_production_settings(settings)

    joined = " ".join(logged)
    assert "SITE_PASSWORD coincide" in joined
    assert "SESSION_SECRET tiene menos de 32" in joined


def test_validate_production_accepts_strong_config(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    settings = Settings(
        site_password="a-very-strong-local-password",
        session_secret="x" * 32,
        openai_api_key="sk-test",
        database_url="postgresql+psycopg://x",
        session_cookie_secure=True,
        dev_auto_login=False,
        app_debug=False,
    )
    validate_production_settings(settings)


def test_validate_production_warns_short_password_under_16_chars(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    settings = Settings(
        site_password="twelve-chars!",
        session_secret="x" * 32,
        openai_api_key="sk-test",
        database_url="postgresql+psycopg://x",
        session_cookie_secure=True,
        dev_auto_login=False,
        app_debug=False,
    )
    logged: list[str] = []

    def _record(msg: str, *args: object) -> None:
        logged.append(msg % args if args else msg)

    monkeypatch.setattr("src.security.logger.warning", _record)
    validate_production_settings(settings)
    assert any("16 caracteres" in line for line in logged)


def test_security_headers_include_csp():
    headers = security_headers()
    assert "Content-Security-Policy" in headers
    assert "default-src 'self'" in headers["Content-Security-Policy"]


def test_audit_portal_csp_allows_cdn_assets():
    from src.security import security_headers_for_path

    csp = security_headers_for_path("/auditoria/")["Content-Security-Policy"]
    assert "cdn.tailwindcss.com" in csp
    assert "cdnjs.cloudflare.com" in csp


def test_health_reports_twilio_flag(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("SITE_PASSWORD", "")

    from httpx import ASGITransport, AsyncClient

    from src.main import app

    async def _run():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/health")

    import asyncio

    response = asyncio.run(_run())
    assert response.status_code == 200
    body = response.json()
    assert "twilio_configured" in body
    assert body["twilio_configured"] is False
    get_settings.cache_clear()
