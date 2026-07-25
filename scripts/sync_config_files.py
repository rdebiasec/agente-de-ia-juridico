#!/usr/bin/env python3
"""Sincroniza prompts/guardrails/skills entre archivos de texto y el config store.

Postgres es autoritativo en runtime; este script permite editar en un editor de
texto y llevar el cambio a la DB (--apply), o traer a disco lo editado en el
portal de auditoría (--export). Ante conflicto (archivo y portal cambiaron) falla
sin escribir nada.

    python scripts/sync_config_files.py --check
    python scripts/sync_config_files.py --apply --author abogada@despacho.com
    python scripts/sync_config_files.py --export
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXIT_OK = 0
EXIT_DRIFT = 1
EXIT_BLOCKED = 2

_LABELS = {
    "in_sync": "sincronizado",
    "file_ahead": "archivo más nuevo → importar a DB",
    "db_ahead": "DB más nueva → exportar a archivo",
    "conflict": "CONFLICTO: archivo y DB cambiaron",
    "no_db": "solo en archivo → crear v1 en DB",
    "no_file": "solo en DB → crear archivo",
    "missing": "sin archivo ni DB",
    "unknown": "indeterminado (falta baseline de header)",
}


def _print_table(diffs: list, *, only_drift: bool) -> None:
    rows = [d for d in diffs if not only_drift or d.status != "in_sync" or d.header_stale]
    if not rows:
        print("Todo sincronizado.")
        return
    width = max(len(f"{d.kind}/{d.key}") for d in rows)
    for d in sorted(rows, key=lambda x: (x.status, x.kind, x.key)):
        label = _LABELS.get(d.status, d.status)
        if d.header_stale:
            label += " (header desactualizado)"
        versions = f"archivo v{d.header_version if d.header_version is not None else '—'} · DB v{d.db_version}"
        print(f"  {f'{d.kind}/{d.key}':<{width}}  {label}  [{versions}]")
        if d.detail and d.status != "in_sync":
            print(f"  {'':<{width}}  ↳ {d.detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="solo reportar diferencias (default)")
    mode.add_argument("--apply", action="store_true", help="importar archivos editados a la DB")
    mode.add_argument("--export", action="store_true", help="escribir a disco lo activo en la DB")
    parser.add_argument("--author", default="", help="email autor del cambio (obligatorio con --apply)")
    parser.add_argument("--note", default="", help="nota para el historial de versiones")
    parser.add_argument(
        "--kind",
        action="append",
        choices=["prompt", "guardrail", "skill"],
        help="limitar a un tipo (repetible)",
    )
    parser.add_argument("--key", action="append", help="limitar a una key concreta (repetible)")
    parser.add_argument("--json", action="store_true", help="salida en JSON")
    parser.add_argument(
        "--allow-conflicts",
        action="store_true",
        help="no fallar por conflictos; los omite y sincroniza el resto",
    )
    args = parser.parse_args()

    if args.apply and not args.author:
        parser.error("--apply requiere --author con un email")

    from src.config_store import export_to_file, import_to_db, iter_diffs, refresh_header
    from src.config_store.sync import BLOCKING, EXPORTABLE, IMPORTABLE

    kinds = tuple(args.kind) if args.kind else None
    diffs = list(iter_diffs(kinds))
    if args.key:
        wanted = set(args.key)
        diffs = [d for d in diffs if d.key in wanted]

    blocked = [d for d in diffs if d.status in BLOCKING]
    actions: list[dict] = []
    exit_code = EXIT_OK

    if args.apply or args.export:
        if blocked and not args.allow_conflicts:
            if args.json:
                print(json.dumps({"blocked": [d.as_dict() for d in blocked]}, ensure_ascii=False, indent=2))
            else:
                print("Conflictos sin resolver — no se escribió nada:\n")
                _print_table(blocked, only_drift=False)
                print(
                    "\nResuelva y reintente:"
                    "\n  · para quedarse con el archivo: --allow-conflicts (omite) o edite en el portal"
                    "\n  · para quedarse con la DB:      --export --allow-conflicts"
                )
            return EXIT_BLOCKED

        targets = IMPORTABLE if args.apply else EXPORTABLE
        for d in diffs:
            if d.status in BLOCKING:
                continue
            try:
                if d.status in targets:
                    result = import_to_db(d, author_email=args.author, note=args.note) if args.apply else export_to_file(d)
                    actions.append({"action": "import" if args.apply else "export", **result})
                elif refresh_header(d):
                    actions.append({"action": "header", "kind": d.kind, "key": d.key, "version": d.db_version})
            except Exception as exc:  # noqa: BLE001 - reportar y continuar con el resto
                actions.append({"action": "error", "kind": d.kind, "key": d.key, "error": str(exc)})
                exit_code = EXIT_BLOCKED

        if args.json:
            print(json.dumps({"actions": actions, "skipped": [d.as_dict() for d in blocked]}, ensure_ascii=False, indent=2))
        else:
            written = [a for a in actions if a["action"] in {"import", "export"}]
            headers = [a for a in actions if a["action"] == "header"]
            errors = [a for a in actions if a["action"] == "error"]
            verb = "Importados a DB" if args.apply else "Exportados a archivo"
            print(f"{verb}: {len(written)}")
            for a in written:
                print(f"  · {a['kind']}/{a['key']} → v{a['version']}")
            if headers:
                print(f"Headers actualizados: {len(headers)}")
            if blocked:
                print(f"Omitidos por conflicto: {len(blocked)}")
                _print_table(blocked, only_drift=False)
            for a in errors:
                print(f"  ! {a['kind']}/{a['key']}: {a['error']}")
        return exit_code

    drift = [d for d in diffs if d.status != "in_sync" or d.header_stale]
    if args.json:
        print(json.dumps({"items": [d.as_dict() for d in diffs]}, ensure_ascii=False, indent=2))
    else:
        print(f"Config store: {len(diffs)} items revisados\n")
        _print_table(diffs, only_drift=True)
    if blocked:
        return EXIT_BLOCKED
    return EXIT_DRIFT if drift else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
