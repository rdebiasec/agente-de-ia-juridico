"""Tests de hash SITE_PASSWORD y webhook Twilio StatusCallback."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.auth.passwords import hash_password, is_password_hash, verify_password
from src.main import app
from src.services.twilio_notify import handle_sms_status_callback, resolve_status_callback_url


def test_password_hash_roundtrip():
    hashed = hash_password("test-secret-pass-long")
    assert is_password_hash(hashed)
    assert verify_password(hashed, "test-secret-pass-long")
    assert not verify_password(hashed, "wrong-pass")


def test_password_plain_legacy_still_works():
    assert verify_password("test-secret-pass", "test-secret-pass")
    assert not verify_password("test-secret-pass", "nope")


@pytest.mark.asyncio
async def test_login_accepts_hashed_site_password(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    hashed = hash_password("test-secret-pass")
    monkeypatch.setenv("SITE_PASSWORD", hashed)
    monkeypatch.setenv("SITE_USERNAME", "despacho")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret-key-32chars")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/auth/login",
            json={"username": "despacho", "password": "test-secret-pass", "accept_privacy": True, "accept_sensitive_data": True},
        )
        assert login.status_code == 200
        assert login.cookies.get("agente_session")

    get_settings.cache_clear()


def test_resolve_status_callback_from_render_url(monkeypatch):
    monkeypatch.delenv("TWILIO_STATUS_CALLBACK", raising=False)
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://app.example.onrender.com")
    from src.config import get_settings

    get_settings.cache_clear()
    assert resolve_status_callback_url() == "https://app.example.onrender.com/twilio/sms-status"
    get_settings.cache_clear()


def test_handle_sms_status_callback_shape():
    result = handle_sms_status_callback(
        {
            "MessageSid": "SM" + "c" * 32,
            "MessageStatus": "delivered",
        }
    )
    assert result["status"] == "delivered"
    assert result["message_sid"].startswith("SM")


@pytest.mark.asyncio
async def test_twilio_sms_status_rejects_bad_signature(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test-auth-token")
    monkeypatch.setattr(
        "src.gateway.twilio_webhook.verify_twilio_request",
        lambda *a, **k: False,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/twilio/sms-status",
            data={"MessageSid": "SMabc", "MessageStatus": "sent"},
            headers={"X-Twilio-Signature": "bad"},
        )
        assert res.status_code == 401

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_twilio_sms_status_accepts_valid_signature(monkeypatch):
    from src.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test-auth-token")
    monkeypatch.setattr(
        "src.gateway.twilio_webhook.verify_twilio_request",
        lambda *a, **k: True,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/twilio/sms-status",
            data={"MessageSid": "SM" + "d" * 32, "MessageStatus": "delivered"},
            headers={"X-Twilio-Signature": "ok"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["status"] == "delivered"

    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_debug_client_log_removed():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/debug/client-log", json={"message": "x"})
        assert res.status_code in {404, 401, 405}
