#!/usr/bin/env python3
"""F-03 — Scorecard estructural de skills (Fuentes KB, Used By, No duplicar, tools).

Calcula ejes deterministas (no juicio jurídico). Exit 1 si algún skill < umbral.

Uso:
  python scripts/score_skill_quality.py
  python scripts/score_skill_quality.py --json
  python scripts/score_skill_quality.py --min-score 4
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

sys.path.insert(0, str(ROOT / "scripts"))
from lib.catalogo_aprobacion import SKILLS_DIR  # noqa: E402

from src.agents.orchestrator import SPECIALIST_AGENT_IDS  # noqa: E402
from src.mcp.tools import REAL_FUNCTION_TOOL_NAMES  # noqa: E402

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

AXES = (
    "fuentes_kb",
    "used_by",
    "no_duplicar",
    "steps",
    "tools_honesty",
)


def _function_tools(text: str) -> list[str]:
    body = text.split("---", 2)[-1] if "---" in text[:80] else text
    m = re.search(r"## Tools\n(.*?)(?=\n## |\Z)", body, re.S)
    if not m:
        return []
    section = m.group(1)
    ft = re.search(r"### Function tools[^\n]*\n(.*?)(?=\n### |\Z)", section, re.S)
    src = ft.group(1) if ft else section
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


def score_skill(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    skill_id = path.parent.name
    axis: dict[str, int] = {}
    notes: list[str] = []

    axis["fuentes_kb"] = 5 if "## Fuentes KB" in text else 1
    if axis["fuentes_kb"] < 5:
        notes.append("falta ## Fuentes KB")

    axis["used_by"] = 5 if "## Used By Agents" in text else 1
    if axis["used_by"] < 5:
        notes.append("falta ## Used By Agents")

    axis["no_duplicar"] = 5 if "## No duplicar" in text else 1
    if axis["no_duplicar"] < 5:
        notes.append("falta ## No duplicar")

    axis["steps"] = 5 if "## Steps" in text else 2
    if axis["steps"] < 5:
        notes.append("falta ## Steps")

    declared = _function_tools(text)
    ghosts = [n for n in declared if n not in ALLOWLIST]
    if not declared:
        axis["tools_honesty"] = 4
    elif ghosts:
        axis["tools_honesty"] = 1
        notes.append(f"tools fantasma: {ghosts}")
    else:
        axis["tools_honesty"] = 5

    avg = round(sum(axis[a] for a in AXES) / len(AXES), 2)
    return {
        "skill_id": skill_id,
        "axes": axis,
        "score": avg,
        "notes": notes,
        "function_tools": declared,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Salida JSON completa")
    parser.add_argument(
        "--min-score",
        type=float,
        default=4.0,
        help="Umbral mínimo (default 4.0)",
    )
    args = parser.parse_args()

    rows = [score_skill(p) for p in sorted(SKILLS_DIR.glob("*/SKILL.md"))]
    below = [r for r in rows if r["score"] < args.min_score]
    summary = {
        "total": len(rows),
        "min_score": args.min_score,
        "below_threshold": len(below),
        "mean_score": round(sum(r["score"] for r in rows) / max(len(rows), 1), 3),
        "skills": rows if args.json else None,
        "offenders": [
            {"skill_id": r["skill_id"], "score": r["score"], "notes": r["notes"]}
            for r in below
        ],
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(
            f"skills={summary['total']} mean={summary['mean_score']} "
            f"below<{args.min_score}={summary['below_threshold']}"
        )
        for off in summary["offenders"][:20]:
            print(f"  - {off['skill_id']}: {off['score']} {off['notes']}")
    return 1 if below else 0


if __name__ == "__main__":
    raise SystemExit(main())
