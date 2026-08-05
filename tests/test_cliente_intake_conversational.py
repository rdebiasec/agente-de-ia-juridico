"""Intake conversacional inmediato en canal víctima."""

from __future__ import annotations

from src.services.cliente_reply_draft import build_intake_visible_reply


def test_intake_asks_questions_and_stays_non_legalistic():
    text = build_intake_visible_reply(
        "Me amenazaron por WhatsApp y tengo evidencia pero no tengo plata. Quiero justicia.",
        display_name="Ector David Lopez",
        prior_cliente_messages=0,
    )
    assert "Ector" in text
    assert "amenaz" in text.lower() or "hostig" in text.lower() or "situación" in text.lower()
    assert "?" in text or "¿" in text
    assert "radicado" not in text.lower()
    assert "garantizamos" not in text.lower()
    assert "155" in text or "ciudad" in text.lower() or "denunci" in text.lower()


def test_intake_impatience_followup():
    text = build_intake_visible_reply(
        "aja y ya?",
        display_name="Ector",
        prior_cliente_messages=1,
    )
    assert "aquí sigo" in text.lower() or "siguiendo" in text.lower() or "armando" in text.lower()
    assert "¿" in text or "?" in text
