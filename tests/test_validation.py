"""Tests de validación Fase 0 — probes dinámicos y rúbrica."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.validation.rubric import total_weight
from src.validation.probes import generate_probes


@pytest.mark.asyncio
async def test_validation_rubric():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/validation/rubric")
    assert r.status_code == 200
    data = r.json()
    assert data["total_weight"] == 100
    assert len(data["blocks"]) == 5
    assert data["connection"]["weight"] == 10


def test_rubric_weights_sum_to_100():
    assert total_weight() == 100


@pytest.mark.asyncio
async def test_generate_probes_fallback():
    result = await generate_probes(user_id="test-py", probes_per_block=2)
    assert "session_id" in result
    assert result["source"] in ("fallback", "llm")
    assert "profile" in result["blocks"]
    assert len(result["blocks"]["profile"]) >= 1


@pytest.mark.asyncio
async def test_generate_probes_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/validation/generate-probes",
            json={"user_id": "test-api", "probes_per_block": 2},
        )
    assert r.status_code == 200
    data = r.json()
    assert "blocks" in data
    assert "areas" in data["blocks"]


@pytest.mark.asyncio
async def test_chat_page_has_score_ui():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/")
    assert r.status_code == 200
    assert "validation-score" in r.text
    assert "Generar Nuevas Preguntas" in r.text
