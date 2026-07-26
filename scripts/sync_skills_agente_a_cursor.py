#!/usr/bin/env python3
"""Espeja skills canónicos `agente/skills` → `.cursor/skills`.

Fuente de verdad runtime/CI: `agente/skills`.
`.cursor/skills` es espejo para el IDE (Cursor Agent Skills); regenerar con este script.

Uso:
  python scripts/sync_skills_agente_a_cursor.py
  python scripts/sync_skills_agente_a_cursor.py --check
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "agente" / "skills"
DST = ROOT / ".cursor" / "skills"


def sync(*, check_only: bool) -> int:
    if not SRC.is_dir():
        print(f"ERROR: no existe fuente canónica {SRC}", file=sys.stderr)
        return 2
    drift: list[str] = []
    for skill_md in sorted(SRC.glob("*/SKILL.md")):
        sid = skill_md.parent.name
        dest = DST / sid / "SKILL.md"
        if not dest.is_file() or not filecmp.cmp(skill_md, dest, shallow=False):
            drift.append(sid)
            if not check_only:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(skill_md, dest)
    # orphan mirrors
    for dest_md in sorted(DST.glob("*/SKILL.md")):
        sid = dest_md.parent.name
        if not (SRC / sid / "SKILL.md").is_file():
            drift.append(f"orphan:{sid}")
            if not check_only:
                dest_md.unlink()
    if check_only:
        if drift:
            print(f"DRIFT ({len(drift)}): {', '.join(drift[:20])}")
            return 1
        print("OK: .cursor/skills espeja agente/skills")
        return 0
    print(f"Sincronizados {len(list(SRC.glob('*/SKILL.md')))} skills → .cursor/skills")
    if drift:
        print(f"Actualizados/limpiados: {len(drift)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="solo reportar drift (exit 1 si diverge)",
    )
    args = parser.parse_args()
    return sync(check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
