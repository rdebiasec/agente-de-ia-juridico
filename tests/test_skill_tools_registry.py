"""Ola 0: SKILL.md no declara function tools fantasma."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.catalogo_aprobacion import SKILLS_DIR, parse_skill_md  # noqa: E402
from src.agents.orchestrator import SPECIALIST_AGENT_IDS  # noqa: E402
from src.mcp.tools import REAL_FUNCTION_TOOL_NAMES  # noqa: E402

# Side-effects documentados (código, no LLM tools).
DOCUMENTED_SIDE_EFFECTS = frozenset(
    {
        "gerencia_ledger",
        "audit_trace",
        "assess_urgency",
        "assess_completeness",
        "record_specialist_result",
        "tareas_gerencia",
        "persist_verification",
    }
)

ALLOWLIST = REAL_FUNCTION_TOOL_NAMES | SPECIALIST_AGENT_IDS | DOCUMENTED_SIDE_EFFECTS


def _function_tools_from_skill(text: str) -> list[str]:
    body = text.split("---", 2)[-1] if text.startswith("---") else text
    m = re.search(r"## Tools\n(.*?)(?=\n## |\Z)", body, re.S)
    if not m:
        return []
    section = m.group(1)
    ft = re.search(r"### Function tools[^\n]*\n(.*?)(?=\n### |\Z)", section, re.S)
    src = ft.group(1) if ft else section
    # Si no hay subsección Function tools, solo aceptar allowlist (legado).
    names: list[str] = []
    for line in src.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        if "no implementad" in line.lower() or "planned" in line.lower():
            continue
        for name in re.findall(r"`([^`]+)`", line):
            if name and name not in names:
                names.append(name)
    return names


def test_canonical_skills_dir_is_agente():
    assert SKILLS_DIR == ROOT / "agente" / "skills"
    assert SKILLS_DIR.is_dir()


def test_skill_function_tools_are_allowlisted():
    ghosts: dict[str, list[str]] = {}
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        # Solo validar sección Function tools (Planned puede listar aspiracionales).
        body = text.split("---", 2)[-1] if text.lstrip().startswith("---") or "---" in text[:80] else text
        m = re.search(r"## Tools\n(.*?)(?=\n## |\Z)", body, re.S)
        if not m:
            continue
        section = m.group(1)
        ft = re.search(r"### Function tools[^\n]*\n(.*?)(?=\n### |\Z)", section, re.S)
        if not ft:
            # Legado sin subsección: todos los `- \`name\`` cuentan
            declared = _function_tools_from_skill(text)
        else:
            declared = []
            for line in ft.group(1).splitlines():
                line = line.strip()
                if not line.startswith("-"):
                    continue
                for name in re.findall(r"`([^`]+)`", line):
                    if name and name not in declared:
                        declared.append(name)
        bad = [n for n in declared if n not in ALLOWLIST]
        if bad:
            ghosts[path.parent.name] = bad
    assert ghosts == {}, f"Tools fantasma en Function tools: {ghosts}"


def test_parse_skill_md_prefers_function_tools_section():
    data = parse_skill_md(SKILLS_DIR / "redactar_memorial_penal" / "SKILL.md")
    tools = data.get("tools") or []
    assert "buscar_en_expediente" in tools
    assert "rag_plantillas_search" not in tools


def test_planned_section_documents_non_real_escape_hatch():
    """F-11: Planned puede listar aspiracionales; Function tools no."""
    from src.mcp.tools import REAL_FUNCTION_TOOL_NAMES

    planned_only_ok = 0
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        body = text.split("---", 2)[-1] if "---" in text[:120] else text
        m = re.search(r"## Tools\n(.*?)(?=\n## |\Z)", body, re.S)
        if not m:
            continue
        pl = re.search(
            r"### Planned capabilities[^\n]*\n(.*?)(?=\n### |\Z)", m.group(1), re.S
        )
        if not pl:
            continue
        for line in pl.group(1).splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue
            for name in re.findall(r"`([^`]+)`", line):
                if name not in REAL_FUNCTION_TOOL_NAMES:
                    planned_only_ok += 1
    assert planned_only_ok >= 1


def test_cursor_mirror_optional_sync_script_exists():
    script = ROOT / "scripts" / "sync_skills_agente_a_cursor.py"
    assert script.is_file()
