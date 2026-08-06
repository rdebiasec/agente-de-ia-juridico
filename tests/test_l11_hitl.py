"""L11 — Guardrails + Human Review: el loop HITL debe materializar borrador."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.storage import get_repository

DRAFTING_MESSAGE = (
    "Redacte un memorial de impulso procesal. "
    "Radicado 11001-60-00-2026-123456. La víctima denunció lesiones. "
    "Tengo poder firmado. Última actuación: audiencia de imputación. "
    "Partes: víctima y procesado."
)


@pytest.mark.asyncio
async def test_l11_drafting_creates_persisted_hitl_draft():
    """Redacción de alto riesgo ⇒ plan HITL ⇒ borrador materializado en el repo."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        offered = await client.post(
            "/chat",
            json={
                "message": DRAFTING_MESSAGE,
                "channel": "web",
                "user_id": "l11-hitl-draft",
            },
        )
        assert offered.status_code == 200
        offered_body = offered.json()
        assert offered_body["pending_review"] is True
        assert offered_body.get("offer_plan") is True

        created = await client.post(
            "/chat/plan",
            json={
                "message": DRAFTING_MESSAGE,
                "channel": "web",
                "user_id": "l11-hitl-draft",
            },
        )
        assert created.status_code == 200
        plan_id = created.json()["plan_id"]

        executed = await client.post(
            f"/chat/plan/{plan_id}/approve-and-execute",
            json={"user_id": "l11-hitl-draft"},
        )
        assert executed.status_code == 200
        data = executed.json()

    assert data.get("pending_review") is True or data.get("draft_id")
    draft_id = data.get("draft_id")
    assert draft_id, "L11 exige borrador materializado cuando hay revisión humana"

    draft = get_repository().get_draft(draft_id)
    assert draft is not None
    assert draft.estado in {"propuesto", "en_revision"}

    actions = (data.get("trace") or {}).get("actions") or []
    assert any(
        a.get("type") == "draft_created" and a.get("status") == "pending" for a in actions
    )
    steps = (data.get("trace") or {}).get("steps") or []
    assert any(
        step.get("step") == "Revisión humana" and step.get("status") == "pending"
        for step in steps
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
