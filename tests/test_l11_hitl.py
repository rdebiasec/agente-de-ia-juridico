"""L11 — Guardrails + Human Review: el loop HITL debe materializar borrador."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.storage import get_repository


@pytest.mark.asyncio
async def test_l11_drafting_creates_persisted_hitl_draft():
    """Redacción en web ⇒ pending_review + draft_id real en el repo."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/chat",
            json={
                "message": "Redacte un correo formal al cliente sobre próximos pasos.",
                "channel": "web",
                "user_id": "l11-hitl-draft",
            },
        )
    assert res.status_code == 200
    data = res.json()
    assert data["pending_review"] is True
    draft_id = data.get("draft_id")
    assert draft_id, "L11 exige borrador materializado cuando hay revisión humana"

    draft = get_repository().get_draft(draft_id)
    assert draft is not None
    assert draft.estado in {"propuesto", "en_revision"}

    actions = (data.get("trace") or {}).get("actions") or []
    assert any(
        a.get("type") == "draft_created" and a.get("status") == "pending" for a in actions
    )
    assert any(
        a.get("type") == "human_review" and a.get("status") == "pending" for a in actions
    )


@pytest.mark.asyncio
async def test_l11_trivial_consult_skips_hitl_draft():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/chat",
            json={
                "message": "Necesito asesoría sobre un arrendamiento habitacional.",
                "channel": "web",
                "user_id": "l11-hitl-skip",
            },
        )
    assert res.status_code == 200
    data = res.json()
    assert data["pending_review"] is False
    assert not data.get("draft_id")


@pytest.mark.asyncio
async def test_l11_poc_output_flags_unmarked_citations():
    from src.agents.sdk_guardrails import poc_output_guardrail

    dirty = await poc_output_guardrail.guardrail_function(
        None, None, "Según el art. 229 y el radicado 1100160000002024001 procede tutela."
    )
    assert dirty.tripwire_triggered is False
    assert dirty.output_info.get("invention_suspect") is True

    clean = await poc_output_guardrail.guardrail_function(
        None,
        None,
        "Posible tipicidad [PENDIENTE DE VERIFICAR] art. 229; radicado [PENDIENTE].",
    )
    assert clean.output_info.get("invention_suspect") is False
    assert clean.output_info.get("pending_markers_count", 0) >= 1
