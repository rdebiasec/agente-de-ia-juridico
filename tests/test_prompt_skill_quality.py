"""Regresión de calidad de prompts/skills (ola multi-experto).

Aserciones deterministas: fallan si vuelve la description genérica,
si analista_evidencia pierde misión, o si reaparecen IDs legacy en Rol en.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "agente" / "skills"
PROMPTS = ROOT / "agente" / "prompts" / "agents"

LEGACY_ROL = {
    "coordinador",
    "analista_cronologia",
    "analista_tipicidad",
    "preparador_audiencias",
    "gestor_evidencia",
    "gestor_seguimiento",
    "redactor",
    "calidad",
    "representacion_victima",
}

DEAD_DESC = "Use when the workflow requires"


def test_no_dead_skill_descriptions():
    offenders = []
    for path in SKILLS.glob("*/SKILL.md"):
        text = path.read_text(encoding="utf-8")
        if DEAD_DESC in text:
            offenders.append(path.parent.name)
    assert offenders == [], f"Descriptions genéricas en: {offenders}"


def test_all_skills_have_no_duplicar():
    missing = [
        p.parent.name
        for p in SKILLS.glob("*/SKILL.md")
        if "## No duplicar" not in p.read_text(encoding="utf-8")
    ]
    assert missing == []


def test_all_skills_have_fuentes_kb():
    """F-05/F-06: ancla procedural obligatoria en skills canónicos."""
    missing = [
        p.parent.name
        for p in SKILLS.glob("*/SKILL.md")
        if "## Fuentes KB" not in p.read_text(encoding="utf-8")
    ]
    assert missing == [], f"Skills sin ## Fuentes KB: {missing}"


_ART_NUM = re.compile(r"\bart\.?\s*\d+", re.I)
_ART_OK = re.compile(
    r"PENDIENTE\s+DE\s+VERIFICAR|conocimiento/|norma\s+verificada|"
    r"sin\s+inventar|no\s+inventar|no\s+citar|no\s+sembrar",
    re.I,
)


def test_skills_and_agent_prompts_do_not_seed_bare_article_numbers():
    """F-06: no sembrar art. N sin path KB o marca pendiente (anti-alucinación)."""
    offenders: list[str] = []
    paths = list(SKILLS.glob("*/SKILL.md")) + list(PROMPTS.glob("*.md"))
    for path in paths:
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not _ART_NUM.search(line):
                continue
            if _ART_OK.search(line):
                continue
            rel = path.relative_to(ROOT)
            offenders.append(f"{rel}:{i}:{line.strip()[:100]}")
    assert offenders == [], "Citas art. N sin ancla/pendiente:\n" + "\n".join(offenders[:20])


def test_no_legacy_rol_en_headers():
    hits = []
    for path in SKILLS.glob("*/SKILL.md"):
        for m in re.finditer(r"^## Rol en (.+)$", path.read_text(encoding="utf-8"), re.M):
            name = m.group(1).strip()
            if name in LEGACY_ROL:
                hits.append(f"{path.parent.name}:{name}")
    assert hits == []


def test_analista_evidencia_prompt_has_mission_and_format():
    text = (PROMPTS / "analista_evidencia.md").read_text(encoding="utf-8")
    assert "## mision" in text
    assert "InventarioEvidencia" in text
    assert "## limites" in text
    assert "## few_shot_backoffice" in text
    assert text.count("**Entrada") >= 2
    assert len(text.splitlines()) >= 40


def test_specialists_have_shared_blocks_and_two_shots():
    specialists = [
        "analista_cronologia_hechos",
        "analista_responsabilidad_tipicidad",
        "analista_ruta_procesal",
        "analista_representacion_victimas",
        "analista_evidencia",
        "analista_audiencias",
        "redactor_documentos_juridicos",
        "analista_seguimiento_procesal",
        "analista_calidad_juridica",
    ]
    for agent_id in specialists:
        text = (PROMPTS / f"{agent_id}.md").read_text(encoding="utf-8")
        assert "## notas_especialista" in text, agent_id
        assert "## deliberacion_discutible" in text, agent_id
        assert text.count("**Entrada") >= 2, agent_id


def test_skill_descriptions_mention_contrato_or_activar():
    """Trigger description útil (no plantilla muerta)."""
    weak = []
    for path in SKILLS.glob("*/SKILL.md"):
        m = re.search(r"^description:\s*(.+)$", path.read_text(encoding="utf-8"), re.M)
        assert m, path
        desc = m.group(1)
        if "Contrato penal" not in desc and "Activar cuando" not in desc:
            weak.append(path.parent.name)
    assert weak == [], f"Descriptions débiles: {weak[:10]}"


def test_cursor_skills_mirror_in_sync():
    """Espejo IDE alineado con canónico (tras sync)."""
    import filecmp

    drift = []
    for src in SKILLS.glob("*/SKILL.md"):
        dst = ROOT / ".cursor" / "skills" / src.parent.name / "SKILL.md"
        if not dst.is_file() or not filecmp.cmp(src, dst, shallow=False):
            drift.append(src.parent.name)
    # Allow empty if sync not run yet in same session — test runs after sync in CI path.
    # Here we require sync: the ola3 step runs sync before pytest.
    assert drift == [], f"Drift espejo .cursor/skills: {drift[:15]}"
