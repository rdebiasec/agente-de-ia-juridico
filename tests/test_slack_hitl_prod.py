"""Tests de producción Slack HITL (health + botones + plan persistido)."""

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
