"""Runtime — catálogo, reglas de negocio, cadenas críticas y migraciones."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lib.catalogo_aprobacion import AGENTS, SKILLS_DIR, load_skills_catalog  # noqa: E402
from validar_skills_metricas import CHAINS, SkillData, _parse_skill, validate_chain  # noqa: E402

from src.agents.plan_templates import build_templated_steps, classify_plan_template
from src.agents.skill_catalog import (
    VALID_AGENT_IDS,
    primary_skill_for_agent,
    valid_skill_ids,
)


def _load_skills() -> dict[str, SkillData]:
    skills: dict[str, SkillData] = {}
    for p in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        sd = _parse_skill(p)
        skills[sd.sid] = sd
    return skills


def test_valid_skill_ids_count_is_90():
    assert len(valid_skill_ids()) == 90
    catalog = load_skills_catalog()
    assert len(catalog) == 90
    assert valid_skill_ids() == frozenset(catalog.keys())


def test_all_catalog_agents_have_primary_skill():
    assert len(AGENTS) == 11
    assert len(VALID_AGENT_IDS) == 11
    for agent in AGENTS:
        aid = agent["id"]
        skill = primary_skill_for_agent(aid)
        assert skill is not None, f"Sin skill primario para {aid}"
        assert skill in valid_skill_ids(), f"Skill inválido {skill} para {aid}"


@pytest.mark.parametrize(
    ("message", "kind", "expect_steps"),
    [
        ("Evaluar acción de tutela por derecho fundamental", "tutela", True),
        ("Necesito una cronología de hechos del caso", "cronologia", True),
        ("Preparar audiencia de juicio oral", "audiencia", True),
        ("Redactar memorial penal de impulso procesal", "indagacion_impulso", True),
        ("Querella por injuria y procedimiento abreviado", "querella_abreviado", True),
        ("Violencia intrafamiliar y medidas de protección", "vif_proteccion", True),
    ],
)
def test_plan_templates_classify_and_build_valid_skills(message: str, kind: str, expect_steps: bool):
    assert classify_plan_template(message) == kind
    steps = build_templated_steps(kind, message)
    if not expect_steps:
        assert steps is None
        return
    assert steps is not None
    assert len(steps) >= 1
    for step in steps:
        if step.skill_id:
            assert step.skill_id in valid_skill_ids()


def test_redactar_tutela_not_used_by_evaluador():
    text = (SKILLS_DIR / "redactar_tutela_penal_preliminar" / "SKILL.md").read_text(encoding="utf-8")
    assert "evaluador_derechos_fundamentales_tutela" not in text.split("## Used By Agents")[1].split("##")[0]


def test_detectar_alucinaciones_no_aprobacion_dictamen():
    text = (SKILLS_DIR / "detectar_alucinaciones_legales" / "SKILL.md").read_text(encoding="utf-8")
    assert "NO ES DICTAMEN DE APROBACIÓN" in text
    assert "Dictamen:" not in text
    assert "clasificar_aprobacion_juridica" in text


def test_ruta_906_no_redacta_recursos_finales():
    text = (SKILLS_DIR / "crear_ruta_procesal_recomendada" / "SKILL.md").read_text(encoding="utf-8")
    assert "redactor_documentos_juridicos_penales" in text
    assert "No redactar memoriales" in text or "No redactar" in text


@pytest.mark.parametrize("chain_name", list(CHAINS.keys()))
def test_critical_chains_ok(chain_name: str):
    skills = _load_skills()
    result = validate_chain(chain_name, CHAINS[chain_name], skills)
    assert result["status"] == "OK", f"{chain_name}: {result['issues']}"


def test_migration_0004_compliance_audit_loads():
    path = ROOT / "migrations" / "versions" / "0004_compliance_audit.py"
    assert path.is_file()
    spec = importlib.util.spec_from_file_location("migration_0004", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.revision == "0004"
    assert callable(mod.upgrade)


def test_migration_0005_execution_plans_loads():
    path = ROOT / "migrations" / "versions" / "0005_execution_plans.py"
    assert path.is_file()
    spec = importlib.util.spec_from_file_location("migration_0005", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.revision == "0005"
    assert callable(mod.upgrade)
