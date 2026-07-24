"""Phase 0 — externalización de prompts/guardrails + config store."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_agent_prompt_files_exist():
    agents = ROOT / "agente" / "prompts" / "agents"
    expected = {
        "coordinador_expediente_penal",
        "analista_cronologia_hechos_penales",
        "analista_tipicidad_y_responsabilidad_penal",
        "analista_ruta_procesal_ley906",
        "analista_representacion_victimas",
        "gestor_evidencia_y_soporte_probatorio",
        "preparador_estrategico_audiencias_penales",
        "redactor_documentos_juridicos_penales",
        "gestor_seguimiento_procesal_penal",
        "evaluador_derechos_fundamentales_tutela",
        "analista_calidad_juridica",
    }
    found = {p.stem for p in agents.glob("*.md")}
    assert expected == found
    for stem in expected:
        assert (agents / f"{stem}.md").read_text(encoding="utf-8").strip()


def test_guardrail_files_match_catalog():
    guard_dir = ROOT / "config" / "guardrails"
    file_ids = {p.stem for p in guard_dir.glob("g*.md")}
    assert file_ids == {f"g{i}" for i in range(1, 11)}
    for gid in file_ids:
        text = (guard_dir / f"{gid}.md").read_text(encoding="utf-8")
        assert f"id: {gid}" in text


def test_orchestrator_loads_external_prompts():
    from src.agents.orchestrator import POC_AGENT_ID, build_orchestrator, get_agent_by_id

    poc = build_orchestrator()
    assert poc.name == POC_AGENT_ID
    assert "COORDINADOR DEL EXPEDIENTE PENAL" in (poc.instructions or "")
    specialist = get_agent_by_id("analista_cronologia_hechos_penales")
    assert specialist is not None
    assert "cronología" in (specialist.instructions or "").lower()
    calidad = get_agent_by_id("analista_calidad_juridica")
    assert calidad is not None
    assert "calidad jurídica" in (calidad.instructions or "").lower()


def test_config_store_save_restore_memory(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    from src.config import get_settings
    from src.storage import reset_repository

    get_settings.cache_clear()
    reset_repository()

    from src.config_store import get_active_content, list_versions, restore_version, save_version

    first = save_version(
        "prompt",
        "analista_calidad_juridica",
        "Rol: calidad v1\nMisión: revisar.",
        author_email="abogada@test.com",
        note="primera",
        expected_version=0,
        write_file=False,
    )
    assert first["version"] == 1
    second = save_version(
        "prompt",
        "analista_calidad_juridica",
        "Rol: calidad v2\nMisión: revisar más.",
        author_email="abogada@test.com",
        note="segunda",
        expected_version=1,
        write_file=False,
    )
    assert second["version"] == 2
    active = get_active_content("prompt", "analista_calidad_juridica")
    assert active["version"] == 2
    assert "v2" in active["content"]
    restored = restore_version(
        "prompt",
        "analista_calidad_juridica",
        1,
        author_email="abogada@test.com",
        write_file=False,
    )
    assert restored["version"] == 3
    active2 = get_active_content("prompt", "analista_calidad_juridica")
    assert "v1" in active2["content"]
    versions = list_versions("prompt", "analista_calidad_juridica")
    assert len(versions) >= 3


def test_config_store_optimistic_lock(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    from src.config import get_settings
    from src.config_store import ConfigConflictError, save_version
    from src.storage import reset_repository

    get_settings.cache_clear()
    reset_repository()

    save_version(
        "guardrail",
        "g1",
        "# No inventar\n\nid: g1\nname: No inventar\n\nTexto A",
        author_email="a@t.com",
        expected_version=0,
        write_file=False,
    )
    with pytest.raises(ConfigConflictError):
        save_version(
            "guardrail",
            "g1",
            "# No inventar\n\nid: g1\nname: No inventar\n\nTexto B",
            author_email="a@t.com",
            expected_version=0,
            write_file=False,
        )

def test_edited_prompt_reaches_orchestrator(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    from src.config import get_settings
    from src.storage import reset_repository

    get_settings.cache_clear()
    reset_repository()

    from src.agents.orchestrator import get_agent_by_id
    from src.config_store import save_version

    marker = "PROMPT_MARKER_RUNTIME_XYZ_99"
    save_version(
        "prompt",
        "analista_calidad_juridica",
        f"Rol: calidad\nMisión: {marker}\n",
        author_email="test@despacho.com",
        expected_version=0,
        write_file=False,
    )
    agent = get_agent_by_id("analista_calidad_juridica")
    assert agent is not None
    assert marker in (agent.instructions or "")
