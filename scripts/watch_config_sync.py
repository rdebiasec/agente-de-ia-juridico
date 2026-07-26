#!/usr/bin/env python3
"""Vigila prompts/guardrails/skills y registra en la DB cada guardado (archivo → config update).

Uso local (con Postgres de Docker ya arriba):

    .venv/bin/python scripts/watch_config_sync.py --author local.owner@dbxsolutions.com

Arranca junto a start-local si CONFIG_FILE_SYNC_WATCH=1 (default).
No usa --allow-conflicts: ante conflicto solo avisa y no escribe.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WATCH_GLOBS = (
    "agente/prompts/**/*.md",
    "config/guardrails/**/*.md",
    ".cursor/skills/*/SKILL.md",
    "agente/skills/*/SKILL.md",
)


def _author_default() -> str:
    return (
        os.environ.get("CONFIG_SYNC_AUTHOR", "").strip()
        or os.environ.get("GIT_AUTHOR_EMAIL", "").strip()
        or "local.dev@localhost"
    )


def _snapshot() -> dict[Path, float]:
    out: dict[Path, float] = {}
    for pattern in WATCH_GLOBS:
        for path in ROOT.glob(pattern):
            if path.is_file():
                try:
                    out[path.resolve()] = path.stat().st_mtime_ns
                except OSError:
                    continue
    return out


def _sync_path(path: Path, *, author: str, note: str) -> None:
    from src.config_store.paths import kind_key_for_path
    from src.config_store.sync import IMPORTABLE, diff_item, import_to_db, refresh_header

    resolved = kind_key_for_path(path)
    if resolved is None:
        return
    kind, key = resolved
    diff = diff_item(kind, key)
    if diff.status in IMPORTABLE:
        result = import_to_db(
            diff,
            author_email=author,
            note=note or f"edición text editor → sync ({diff.status})",
        )
        print(f"✓ {kind}/{key} → v{result['version']} ({diff.status})")
        return
    if refresh_header(diff):
        print(f"↻ {kind}/{key} header → v{diff.db_version}")
        return
    if diff.status == "in_sync":
        return
    print(f"! {kind}/{key}: {diff.status} — {diff.detail or 'sin acción'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--author", default=_author_default(), help="email autor de las versiones")
    parser.add_argument("--note", default="", help="nota fija para el historial (opcional)")
    parser.add_argument("--interval", type=float, default=0.75, help="segundos entre polls")
    parser.add_argument("--once", action="store_true", help="una pasada (aplicar drift actual) y salir")
    args = parser.parse_args()

    if not args.author:
        print("Falta --author o CONFIG_SYNC_AUTHOR", file=sys.stderr)
        return 2

    print(f"Watch config → DB (author={args.author})")
    print("  paths: prompts, guardrails, skills")
    prev = _snapshot()
    if args.once:
        for path in sorted(prev):
            _sync_path(path, author=args.author, note=args.note)
        return 0

    try:
        while True:
            time.sleep(max(0.2, args.interval))
            cur = _snapshot()
            changed = [p for p, mtime in cur.items() if prev.get(p) != mtime]
            # archivos nuevos
            changed.extend(p for p in cur if p not in prev)
            prev = cur
            # debounce: esperar a que dejen de escribir
            if not changed:
                continue
            time.sleep(0.35)
            cur2 = _snapshot()
            prev = cur2
            for path in sorted(set(changed)):
                if path in cur2:
                    try:
                        _sync_path(path, author=args.author, note=args.note)
                    except Exception as exc:  # noqa: BLE001
                        print(f"! error {path.name}: {exc}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nWatch detenido.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
