"""F-03 / F-04 / F-11 / F-07+ — quick wins estructurales (sin auth portal)."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "agente" / "skills"


def test_f03_score_skill_quality_script_passes():
    script = ROOT / "scripts" / "score_skill_quality.py"
    assert script.is_file()
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "below<" in proc.stdout or "mean=" in proc.stdout


def test_f04_diff_agent_contract_script_passes():
    script = ROOT / "scripts" / "diff_agent_contract.py"
    assert script.is_file()
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "failed_p0=0" in proc.stdout


def test_f07_specialist_schemas_expose_fuentes_kb():
    """Groundedness estructural: schemas de especialistas tienen fuentes_kb."""
    from src.agents.schemas import (
        BorradorDocumentoPenal,
        CronologiaPenal,
        DictamenCalidad,
        InventarioEvidencia,
        MatrizTipicidad,
        PreparacionAudiencia,
        RepresentacionVictimas,
        RutaProcesalLey906,
        SeguimientoProcesal,
    )

    for cls in (
        CronologiaPenal,
        MatrizTipicidad,
        RutaProcesalLey906,
        RepresentacionVictimas,
        InventarioEvidencia,
        PreparacionAudiencia,
        BorradorDocumentoPenal,
        DictamenCalidad,
        SeguimientoProcesal,
    ):
        assert "fuentes_kb" in cls.model_fields, cls.__name__
        sample = cls.model_construct(fuentes_kb=["agente/conocimiento/penal.md"])
        assert sample.fuentes_kb[0].startswith("agente/conocimiento/")


def test_f11_planned_section_allows_non_real_names():
    """F-11: escape hatch Planned — nombres fuera de REAL están documentados."""
    from src.mcp.tools import REAL_FUNCTION_TOOL_NAMES

    planned_non_real: list[str] = []
    with_planned = 0
    for path in sorted(SKILLS.glob("*/SKILL.md")):
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
        with_planned += 1
        for line in pl.group(1).splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue
            for name in re.findall(r"`([^`]+)`", line):
                if name not in REAL_FUNCTION_TOOL_NAMES:
                    planned_non_real.append(f"{path.parent.name}:{name}")
    assert with_planned >= 50, f"pocas secciones Planned: {with_planned}"
    assert planned_non_real, "se esperaba al menos 1 tool Planned fuera de REAL"