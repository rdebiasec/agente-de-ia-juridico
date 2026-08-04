"""Mejoras locales: borrador Gerente, calidad, pedidos, inbox."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.storage.memory import InMemoryRepository
from src.storage.models import Expediente


@pytest.fixture()
def repo(monkeypatch):
    mem = InMemoryRepository()
    monkeypatch.setattr("src.storage.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.triple_chat.get_repository", lambda: mem)
    monkeypatch.setattr("src.services.cliente_reply_draft.get_repository", lambda: mem)
    return mem


def test_contextual_draft_uses_expediente(repo):
    from src.services.cliente_reply_draft import contextual_gerente_draft

    repo.save_expediente(
        Expediente(
            session_id="web:abogada",
            radicado="1100160000002024001",
            etapa_actual="indagación",
            rol_despacho="víctimas",
        )
    )
    text = contextual_gerente_draft(
        "¿Cómo va mi denuncia?",
        lawyer_session_id="web:abogada",
    )
    assert "indagación" in text.lower() or "radicado" in text.lower()
    assert "Gerente" in text
    assert "no invent" in text.lower() or "expediente" in text.lower()


def test_quality_flags_harsh_tone():
    from src.services.cliente_reply_draft import quality_check_cliente_draft

    q = quality_check_cliente_draft("Usted mintió y merece castigo. Corto.")
    assert "tono_riesgo_revictimizacion" in q.flags
    assert "[ajuste de tono pendiente]" in q.cleaned_text


def test_enqueue_builds_real_draft_with_quality(repo):
    from src.services.triple_chat import enqueue_client_message, list_cliente_inbox

    out = enqueue_client_message(
        message="Necesito saber el estado de mi caso de violencia",
        cliente_subject="victima-mejora-1",
        lawyer_session_id="web:abogada",
        subject_label="VIF demo",
    )
    assert out["status"] == "en_revision"
    assert out["status_label"]
    assert "draft_id" in out
    assert "quality_flags" in out

    inbox = list_cliente_inbox(status="proposed")
    assert inbox["pending_count"] == 1
    draft = inbox["drafts"][0]
    assert draft["case_label"] == "VIF demo"
    assert "quality_flags" in draft
    assert "Gerente" in draft["proposed_text"] or "despacho" in draft["proposed_text"].lower()


def test_list_cliente_status_labels(repo):
    from src.services.triple_chat import (
        approve_outbound_draft,
        enqueue_client_message,
        list_cliente_visible_messages,
    )

    out = enqueue_client_message(
        message="Consulta estado",
        cliente_subject="victima-status-1",
        lawyer_session_id="web:abogada",
    )
    mid = list_cliente_visible_messages("victima-status-1")
    assert mid["status"] == "en_revision"
    assert "revisión" in mid["status_label"].lower()

    approve_outbound_draft(out["draft_id"], revisor="abogada", edited_text="Respuesta lista del Gerente.")
    after = list_cliente_visible_messages("victima-status-1")
    assert after["status"] == "respuesta_lista"


@pytest.mark.asyncio
async def test_hooks_extract_pedido_from_tool_arguments(repo):
    from src.agents.runner import _TraceRunHooks

    class FakeTool:
        name = "analista_cronologia_hechos"

    class FakeCtx:
        tool_arguments = json.dumps(
            {
                "pedido": "Ordenar hechos del 12-ene",
                "hechos_confirmados": "Denuncia en CAI",
                "etapa": "indagación",
            }
        )

    hooks = _TraceRunHooks(
        {
            "session_id": "web:abogada",
            "trace_id": "tr-pedido",
            "spans": [],
            "actions": [],
            "completion": {"calls": []},
            "input_summary": "consulta abogado",
        }
    )
    await hooks.on_tool_start(FakeCtx(), None, FakeTool())
    await hooks.on_tool_end(FakeCtx(), None, FakeTool(), {"ok": True})
    listed = repo.list_internal_transcript("web:abogada")
    assert listed
    assert "Ordenar hechos" in listed[0].pedido
    assert "Hechos:" in listed[0].pedido or "Denuncia" in listed[0].pedido


def test_desk_and_cliente_ui_markers():
    html = Path("static/desk/abogado.html").read_text(encoding="utf-8")
    assert "cliente-inbox-count" in html
    assert "alerta de calidad" in html.lower() or "calidad" in html.lower()
    assert "Junta del caso" in html

    cliente_js = Path("static/cliente.js").read_text(encoding="utf-8")
    assert "status_label" in cliente_js
    assert "CASO-" in cliente_js
    assert "lexiatek_cliente_pin" in cliente_js
    assert "internal-transcript" not in cliente_js
    assert "Junta del caso" not in cliente_js

    firma_js = Path("static/firma.js").read_text(encoding="utf-8")
    assert "quality_flags" in firma_js
    assert "case_label" in firma_js


def test_list_internal_transcript_includes_junta_fields(repo):
    from src.services.triple_chat import list_internal_transcript, record_specialist_exchange

    record_specialist_exchange(
        session_id="web:abogada",
        specialist_id="analista_calidad_juridica",
        pedido="Revisar borrador",
        respuesta="OK con pendiente",
        turn_ref="tr-junta",
        kind="findings",
        ronda=1,
    )
    listed = list_internal_transcript("web:abogada")
    row = listed["entries"][0]
    assert row["alto_riesgo"] is True
    assert row["specialist_id"] == "analista_calidad_juridica"
    assert row["kind_label"] == "Hallazgos"
