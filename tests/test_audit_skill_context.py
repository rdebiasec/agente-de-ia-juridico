"""Catálogo del portal: contexto auditable por guía (instrucción, tools, guardrails)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.audit_data import build_audit_data  # noqa: E402
from lib.catalogo_aprobacion import guia_audit_key, load_skills_catalog, skill_tools_list  # noqa: E402


# Canon post-retiro de tutela: 81 skills penal-víctimas.
EXPECTED_SKILL_COUNT = 81


def test_build_audit_data_skill_context_fields():
    data = build_audit_data()
    skills = data["skills"]
    assert len(skills) == EXPECTED_SKILL_COUNT

    sample = next(s for s in skills if s["id"] == "extraer_hechos_relevantes")
    assert sample["instruccion"]
    assert sample["purpose"]
    assert sample["rol"]
    assert sample["no_duplicar"]
    assert sample["riesgo"]
    assert sample["tier"] == "operativo"
    assert isinstance(sample["tools"], list)
    assert len(sample["tools"]) >= 1
    assert sample["tools_text"]
    assert isinstance(sample["guardrails"], list)
    assert len(sample["guardrails"]) >= 1
    assert sample["source_path"] == "agente/skills/extraer_hechos_relevantes/SKILL.md"
    assert sample["audit_keys"] == {
        "instruccion": guia_audit_key("extraer_hechos_relevantes", "instruccion"),
        "tools": guia_audit_key("extraer_hechos_relevantes", "tools"),
        "guardrails": guia_audit_key("extraer_hechos_relevantes", "guardrails"),
    }


def test_all_skills_have_three_audit_keys():
    data = build_audit_data()
    for skill in data["skills"]:
        sid = skill["id"]
        keys = skill.get("audit_keys") or {}
        assert keys.get("instruccion") == guia_audit_key(sid, "instruccion")
        assert keys.get("tools") == guia_audit_key(sid, "tools")
        assert keys.get("guardrails") == guia_audit_key(sid, "guardrails")
        assert skill.get("instruccion")
        assert skill.get("steps")


def test_items_total_includes_guia_context():
    data = build_audit_data()
    intro = data["intro"]
    expected = (
        intro["guardrails"]
        + intro["agentes"]
        + intro["guias_contexto"]
        + intro["pasos_total"]
    )
    assert intro["guias_contexto"] == EXPECTED_SKILL_COUNT * 3
    assert intro["items_total"] == expected
    assert data["version"] == "2.1"


def test_catalog_helpers_tools_from_skill_md():
    raw = load_skills_catalog()["extraer_hechos_relevantes"]
    tools = skill_tools_list(raw)
    # Solo function tools implementables; planned/no implementadas no cuentan.
    assert "buscar_en_expediente" in tools
    assert "document_parser_extract_text" not in tools
