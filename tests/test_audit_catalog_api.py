"""API de catálogo vivo del portal de auditoría."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_audit_catalog_live():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/audit/catalog")
        assert r.status_code == 200
        data = r.json()
        assert data["version"] == "2.1"
        assert len(data["skills"]) == 90
        assert len(data["agentes"]) == 11
        assert data["intro"]["items_total"] == data["totals"]["items"]

        sample = next(s for s in data["skills"] if s["id"] == "extraer_hechos_relevantes")
        assert sample["instruccion"]
        assert sample["purpose"]
        assert sample["tools"]
        assert sample["guardrails"]
        assert sample["steps"]
