"""Regresión hallazgos auditoría Gerente G01–G09 (orden sugerido)."""

from __future__ import annotations

import pytest

from src.agents.triage import (
    TriageBundle,
    build_triage_bundle,
    infer_destination_agent,
)


def test_g03_triage_no_roba_tipicidad_con_verificar():
    assert (
        infer_destination_agent("Necesito verificar tipicidad y dolo del caso")
        == "analista_responsabilidad_tipicidad"
    )


def test_g03_triage_borrador_resumen_no_es_redactor():
    dest = infer_destination_agent("Hazme un borrador de resumen de los hechos")
    assert dest != "redactor_documentos_juridicos"
    assert dest in {
        "analista_cronologia_hechos",
        "coordinador_caso",
    }


def test_g03_memorial_sigue_siendo_redactor():
    assert (
        infer_destination_agent("Redáctame un memorial de impulso procesal")
        == "redactor_documentos_juridicos"
    )


def test_g02_triage_bundle_single_pass():
    from src.storage.models import Expediente

    exp = Expediente(session_id="web:g02")
    bundle = build_triage_bundle(
        "Analizar tipicidad del caso",
        expediente=exp,
        destination="analista_responsabilidad_tipicidad",
    )
    assert isinstance(bundle, TriageBundle)
    assert bundle.triage.agente_destino == "analista_responsabilidad_tipicidad"
    assert bundle.completeness is not None
    assert bundle.urgency is not None


@pytest.mark.asyncio
async def test_g01_plan_required_persists_chat_history(monkeypatch):
    from src.agents import runner as runner_mod

    calls: list[tuple[str, str]] = []

    class FakeRepo:
        def get_chat_session(self, _sid):
            return None

        def list_session_traces(self, _sid, limit=40):
            return []

        def append_chat_message(self, session_id, **kwargs):
            calls.append((kwargs.get("role"), kwargs.get("content", "")[:40]))
            return None

        def save_session_trace(self, *a, **k):
            return None

        def mutate_expediente(self, *a, **k):
            return None

    monkeypatch.setattr(runner_mod, "get_repository", lambda: FakeRepo())
    monkeypatch.setattr(
        "src.services.expediente_sync.sync_expediente_from_chat",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "src.agents.completeness.persist_verification",
        lambda *a, **k: None,
    )

    class Exp:
        session_id = "web:g01-persist"
        hechos_minimos_confirmados = True
        poder_acreditado = True
        ultima_actuacion_confirmada = True
        radicado = "1234567890123456789"
        partes = [{"rol": "victima", "nombre": "X"}]
        rol_despacho = "apoderado"
        etapa_actual = "indagacion"
        terminos: list = []
        evidencias: list = []
        faltantes: list = []

        def resumen(self):
            return "radicado 123 hechos mínimos poder última actuación partes"

    monkeypatch.setattr(
        runner_mod.expediente_store,
        "get_or_create",
        lambda _sid: Exp(),
    )

    result = await runner_mod.run_agent(
        "Redáctame un memorial de impulso con los hechos ya aportados",
        channel="web",
        session_id="web:g01-persist",
        user_id="abogada",
    )
    assert result["trace"]["route"] == "plan_required"
    roles = [r for r, _ in calls]
    assert "user" in roles
    assert "assistant" in roles


def test_g04_cronologia_incluye_ruta906():
    from src.agents.orchestrator import _SPECIALIST_NEIGHBORS

    assert "analista_ruta_procesal" in _SPECIALIST_NEIGHBORS[
        "analista_cronologia_hechos"
    ]


def test_g05_cache_stats_expose_max():
    from src.agents.agent_cache import cache_stats

    stats = cache_stats()
    assert stats["orchestrator_max"] == 6


def test_g07_slack_notify_flag_exists():
    from src.config import Settings

    assert "slack_notify_web_drafts" in Settings.model_fields


def test_g08_prompt_parity_parses_header():
    from src.agents.prompt_parity import check_prompt_parity, parse_file_prompt_header

    ver, chk = parse_file_prompt_header(
        "<!-- config-version: 14; checksum: e5b134fe61eac5f4 -->\n# x"
    )
    assert ver == 14
    assert chk == "e5b134fe61eac5f4"
    report = check_prompt_parity()
    assert report["agent_id"] == "coordinador_caso"
    assert report["file_version"] is not None and report["file_version"] >= 1
    assert report["file_checksum"]
    # ok depende de DB local/prod; aquí solo exigimos que el checker responda.
    assert report["status"] in {
        "ok",
        "ok_checksum",
        "db_unavailable",
        "checksum_mismatch",
        "version_mismatch",
        "no_file_header",
        "missing_file",
    }


def test_g08_parity_checksum_wins_over_version_counter(monkeypatch, tmp_path):
    from src.agents import prompt_parity as pp

    layout = tmp_path / "prompts" / "agents"
    layout.mkdir(parents=True)
    (layout / "coordinador_caso.md").write_text(
        "<!-- config-version: 14; checksum: e5b134fe61eac5f4 -->\n# body\n",
        encoding="utf-8",
    )

    class S:
        agente_dir = tmp_path

    monkeypatch.setattr("src.config.get_settings", lambda: S())

    import src.config_store as cs

    monkeypatch.setattr(cs, "KIND_PROMPT", "prompt", raising=False)
    monkeypatch.setattr(
        cs,
        "get_active_content",
        lambda kind, key: {"version": 3, "checksum": "e5b134fe61eac5f4"},
    )

    report = pp.check_prompt_parity()
    assert report["ok"] is True
    assert report["status"] == "ok_checksum"
    assert report["db_version"] == 3
    assert report["file_version"] == 14


def test_g09_udemy_b12_marcado_hecho():
    from pathlib import Path

    text = Path("docs/auditoria/UDEMY_LISTA_CAMBIOS.md").read_text(encoding="utf-8")
    assert "B12" in text
    assert "slack_socket_started=true" in text or "**hecho** (prod" in text
