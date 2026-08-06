"""F4 P0 — traza pública sin system_prompt; auth forzada en prod."""

from __future__ import annotations

import pytest

from src.observability.trace_public import public_trace
from src.security import validate_production_settings


def test_public_trace_redacts_system_prompt():
    raw = {
        "route": "chat",
        "completion": {
            "calls": [
                {
                    "call_id": "cmp-1",
                    "system_prompt": "PROMPT SECRETO DEL SISTEMA",
                    "instructions": "instrucciones internas",
                    "input_preview": "hola",
                }
            ]
        },
    }
    cleaned = public_trace(raw)
    assert cleaned is not None
    call = cleaned["completion"]["calls"][0]
    assert call["system_prompt"] == "[redacted]"
    assert call["instructions"] == "[redacted]"
    assert call["input_preview"] == "hola"
    # Original intacto
    assert raw["completion"]["calls"][0]["system_prompt"] == "PROMPT SECRETO DEL SISTEMA"


def test_production_rejects_web_auth_disabled(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    from src.config import Settings

    settings = Settings(
        site_password="strong-production-password-32",
        session_secret="session-secret-at-least-32-chars-xx",
        openai_api_key="sk-test",
        database_url="postgresql+psycopg://u:p@localhost/db",
        web_auth_enabled=False,
        session_cookie_secure=True,
        dev_auto_login=False,
        app_debug=False,
    )
    with pytest.raises(RuntimeError, match="WEB_AUTH_ENABLED"):
        validate_production_settings(settings)


def test_resolve_web_user_id_blocks_shared_subject_in_prod(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("WEB_AUTH_ENABLED", "false")
    from fastapi import HTTPException

    from src.auth.deps import resolve_web_user_id
    from src.config import Settings, get_settings

    get_settings.cache_clear()
    settings = Settings(
        site_password="",
        session_secret="session-secret-at-least-32-chars-xx",
        session_cookie_secure=True,
        web_auth_enabled=False,
    )
    with pytest.raises(HTTPException) as exc:
        resolve_web_user_id(settings, None, client_fallback="test")
    assert exc.value.status_code == 503
    get_settings.cache_clear()
