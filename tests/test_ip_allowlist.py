"""Tests del middleware IP allowlist."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.middleware.ip_allowlist import ip_is_allowed, parse_allowlist, path_is_bypassed


def test_parse_and_match_allowlist():
    nets = parse_allowlist("66.42.28.38, 10.0.0.0/8")
    assert ip_is_allowed("66.42.28.38", nets, allow_loopback=False) is True
    assert ip_is_allowed("10.1.2.3", nets, allow_loopback=False) is True
    assert ip_is_allowed("8.8.8.8", nets, allow_loopback=False) is False
    assert ip_is_allowed("127.0.0.1", nets, allow_loopback=True) is True


def test_path_bypass():
    assert path_is_bypassed("/health") is True
    assert path_is_bypassed("/slack/interactivity") is True
    assert path_is_bypassed("/twilio/sms-status") is True
    assert path_is_bypassed("/abogado") is False
    assert path_is_bypassed("/auditoria/") is False
    assert path_is_bypassed("/chat") is False


@pytest.mark.asyncio
async def test_middleware_blocks_foreign_ip(monkeypatch):
    from src.config import get_settings

    monkeypatch.setenv("IP_ALLOWLIST_ENABLED", "true")
    monkeypatch.setenv("IP_ALLOWLIST", "66.42.28.38")
    monkeypatch.setenv("WEB_AUTH_ENABLED", "false")
    monkeypatch.setenv("SITE_PASSWORD", "")
    monkeypatch.setenv("RENDER", "true")
    get_settings.cache_clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        denied = await client.get("/abogado", headers={"cf-connecting-ip": "1.2.3.4"})
        assert denied.status_code == 403
        assert denied.json()["code"] == "ip_not_allowed"

        allowed = await client.get("/abogado", headers={"cf-connecting-ip": "66.42.28.38"})
        assert allowed.status_code == 200

        health = await client.get("/health", headers={"cf-connecting-ip": "1.2.3.4"})
        assert health.status_code == 200
        assert health.json().get("ip_allowlist_enabled") is True

        slack = await client.post(
            "/slack/interactivity",
            content=b"payload={}",
            headers={
                "cf-connecting-ip": "1.2.3.4",
                "content-type": "application/x-www-form-urlencoded",
            },
        )
        # Bypass path: no 403 por IP (puede fallar firma Slack, pero no allowlist).
        assert slack.status_code != 403 or slack.json().get("code") != "ip_not_allowed"

    monkeypatch.delenv("RENDER", raising=False)
    get_settings.cache_clear()
