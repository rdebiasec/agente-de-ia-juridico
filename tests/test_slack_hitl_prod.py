"""Tests de producción Slack HITL (health + botones + edición + allowlist)."""

from __future__ import annotations

import pytest


def test_slack_health_flags_shape(monkeypatch):
    from src.channels import slack_status
    from src.config import get_settings

    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "signing")
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-test")
    get_settings.cache_clear()
    slack_status.mark_slack_socket_started(True)
    flags = slack_status.slack_health_flags()
    assert flags["slack_configured"] is True
    assert flags["slack_app_token_configured"] is True
    assert flags["slack_socket_started"] is True
    slack_status.mark_slack_socket_started(False)
    get_settings.cache_clear()


def test_aplicar_accion_borrador_approve_reject(monkeypatch):
    from src.config import get_settings
    from src.gateway.slack_interactivity import aplicar_accion_borrador
    from src.storage import get_repository, reset_repository
    from src.storage.models import ESTADO_EN_REVISION, Draft

    monkeypatch.setenv("DATABASE_URL", "")
    get_settings.cache_clear()
    reset_repository()
    repo = get_repository()
    repo.add_draft(
        Draft(id="tstapr01", session_id="t", titulo="A", contenido="c", estado=ESTADO_EN_REVISION)
    )
    repo.add_draft(
        Draft(id="tstrej01", session_id="t", titulo="R", contenido="c", estado=ESTADO_EN_REVISION)
    )
    ok = aplicar_accion_borrador("draft_aprobar", "tstapr01", revisor="tester")
    bad = aplicar_accion_borrador("draft_rechazar", "tstrej01", revisor="tester")
    assert ok and "aprobado" in ok
    assert bad and "rechazado" in bad
    assert repo.get_draft("tstapr01").estado == "aprobado"
    assert repo.get_draft("tstrej01").estado == "rechazado"
    get_settings.cache_clear()
    reset_repository()


def test_slack_edit_modal_and_apply(monkeypatch):
    from src.config import get_settings
    from src.gateway.slack_interactivity import aplicar_edicion_borrador
    from src.hitl.slack_review import DRAFT_EDIT_CALLBACK, build_edit_modal
    from src.storage import get_repository, reset_repository
    from src.storage.models import ESTADO_EN_REVISION, Draft

    monkeypatch.setenv("DATABASE_URL", "")
    get_settings.cache_clear()
    reset_repository()
    repo = get_repository()
    draft = Draft(
        id="tstedt01",
        session_id="web:sess",
        titulo="Memorial",
        contenido="versión IA",
        estado=ESTADO_EN_REVISION,
    )
    repo.add_draft(draft)
    repo.append_chat_message(
        "web:sess",
        channel="web",
        user_id="abogado",
        role="user",
        content="genera memorial",
        max_messages=50,
    )

    modal = build_edit_modal(draft)
    assert modal["callback_id"] == DRAFT_EDIT_CALLBACK
    assert modal["private_metadata"] == "tstedt01"
    assert "Editar" in str(
        __import__("src.hitl.slack_review", fromlist=["_bloques_revision"])._bloques_revision(
            draft
        )
    )

    msg = aplicar_edicion_borrador(
        "tstedt01",
        revisor="U123|abogada",
        nuevo_contenido="versión abogado",
        comentario="ajusté hechos",
    )
    assert "editado" in msg
    updated = repo.get_draft("tstedt01")
    assert updated.estado == "editado"
    assert updated.contenido == "versión abogado"
    assert updated.revisor == "U123|abogada"
    session = repo.get_chat_session("web:sess")
    assert any("HITL:tstedt01:editado" in (m.get("content") or "") for m in session.messages)
    get_settings.cache_clear()
    reset_repository()


def test_slack_approver_allowlist(monkeypatch):
    from src.config import get_settings
    from src.gateway.slack_interactivity import SlackAuthError, ensure_slack_approver

    monkeypatch.setenv("SLACK_APPROVER_IDS", "UAAA,UBBB")
    get_settings.cache_clear()
    assert ensure_slack_approver({"id": "UAAA", "username": "ana"}) == "UAAA|ana"
    with pytest.raises(SlackAuthError):
        ensure_slack_approver({"id": "UXXX", "username": "otro"})
    monkeypatch.delenv("SLACK_APPROVER_IDS", raising=False)
    get_settings.cache_clear()
    assert ensure_slack_approver({"id": "UXXX", "username": "otro"}) == "UXXX|otro"
