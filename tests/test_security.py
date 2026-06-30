"""Tests de controles de producción y seguridad."""

from __future__ import annotations

import pytest

from src.config import Settings
from src.security import debug_enabled, is_production, validate_production_settings


def test_debug_disabled_in_production(monkeypatch):
    settings = Settings(session_cookie_secure=True, app_debug=True)
    assert is_production(settings) is True
    assert debug_enabled(settings) is False


def test_validate_production_rejects_weak_secrets(monkeypatch):
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
