"""SEC-06/07 — rate limit de planes y redacción SSE."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.agents.plan_executor import _redact_preview
from src.main import app


def test_redact_preview_truncates_and_masks():
    long_text = "contacto@caso.com " + ("x" * 250) + " radicado 12345678901234"
    redacted = _redact_preview({"summary": long_text})
    assert len(redacted["summary"]) <= 201
    assert "[email]" in redacted["summary"]


@pytest.mark.asyncio
async def test_chat_plan_rate_limited(monkeypatch):
    import src.main as main_mod

    monkeypatch.setattr(main_mod, "CHAT_PLAN_RATE_MAX", 2)
    monkeypatch.setattr(main_mod, "CHAT_PLAN_RATE_WINDOW", 900)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for _ in range(2):
            ok = await client.post(
                "/chat/plan",
                json={
                    "message": "Cronología breve del caso.",
                    "channel": "web",
                    "user_id": "rate-user",
                },
            )
            assert ok.status_code == 200

        blocked = await client.post(
            "/chat/plan",
            json={
                "message": "Otro plan.",
                "channel": "web",
                "user_id": "rate-user",
            },
        )
        assert blocked.status_code == 429
