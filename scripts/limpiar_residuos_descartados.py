#!/usr/bin/env python3
"""Limpia residuos de capacidades descartadas (tutela/constitucional, huérfanos, g* legacy).

Acciones:
1. Backup JSON de keys a retirar y filas demo.
2. Retira del config store keys sin archivo en disco (tutela, aliases viejos, etc.).
3. Publica a DB los stubs deprecados g1…g10 y el resto de archivos file_ahead.
4. Borra drafts/deadlines/demo sessions con tipología tutela.
5. Opcional: purga historial de versiones de keys retiradas (default: sí).

Uso:
  # Local
  set -a && source .env && set +a
  python scripts/limpiar_residuos_descartados.py --dry-run
  python scripts/limpiar_residuos_descartados.py --apply --author limpieza@dbxsolutions.com

  # Producción (External Database URL de Render)
  DATABASE_URL='postgresql+psycopg://…' \\
    python scripts/limpiar_residuos_descartados.py --apply --author limpieza@dbxsolutions.com
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Keys retiradas aunque aún exista archivo (defensa en profundidad)
FORCE_RETIRE_SUBSTRINGS = (
    "tutela",
    "constitucional",
    "perjuicio_irremediable",
    "derecho_fundamental",
    "mecanismos_ordinarios",
    "coordinador_expediente_penal",
    "redactor_documentos_juridicos_penales",
    "analista_cronologia_hechos_penales",
    "analista_ruta_procesal_ley906",
    "analista_tipicidad_y_responsabilidad_penal",
    "gestor_evidencia_y_soporte_probatorio",
    "gestor_seguimiento_procesal_penal",
    "preparador_estrategico_audiencias_penales",
)


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = val.strip().strip('"').strip("'")


def _backup_dir() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = ROOT / "tmp" / f"limpieza_residuos_{stamp}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _should_force_retire(key: str) -> bool:
    low = key.lower()
    return any(s in low for s in FORCE_RETIRE_SUBSTRINGS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Solo reportar")
    parser.add_argument("--apply", action="store_true", help="Ejecutar limpieza")
    parser.add_argument("--author", default="limpieza@dbxsolutions.com")
    parser.add_argument("--skip-sync", action="store_true", help="No importar archivos a DB")
    parser.add_argument("--keep-versions", action="store_true", help="No borrar historial config_versions")
    parser.add_argument("--skip-demo-data", action="store_true", help="No tocar drafts/deadlines/sessions")
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        parser.error("Indique --dry-run o --apply")

    _load_dotenv()
    if not os.environ.get("DATABASE_URL"):
        print("ERROR: DATABASE_URL no configurada", file=sys.stderr)
        return 2

    from sqlalchemy import create_engine, text

    from src.config_store import list_orphan_config_keys, retire_config_key
    from src.storage.sql import normalize_database_url

    backup = _backup_dir()
    report: dict = {
        "database_host": (os.environ["DATABASE_URL"].split("@")[-1] if "@" in os.environ["DATABASE_URL"] else "?"),
        "orphans": [],
        "force_retire": [],
        "retired": [],
        "synced": [],
        "demo_deleted": {},
    }

    orphans = list_orphan_config_keys()
    report["orphans"] = [{"kind": k, "key": v} for k, v in orphans]

    # También forzar retiro por nombre aunque hubiera archivo (no debería)
    from src.storage import get_repository

    repo = get_repository()
    force: list[tuple[str, str]] = []
    for active in repo.list_config_active():
        if _should_force_retire(active.key) and (active.kind, active.key) not in orphans:
            force.append((active.kind, active.key))
    report["force_retire"] = [{"kind": k, "key": v} for k, v in force]

    targets = sorted(set(orphans) | set(force))
    print(f"Keys a retirar: {len(targets)}")
    for kind, key in targets:
        print(f"  - {kind}/{key}")

    # Backup contents
    backed = []
    for kind, key in targets:
        versions = repo.list_config_versions(kind, key, limit=100)
        backed.append(
            {
                "kind": kind,
                "key": key,
                "versions": [
                    {
                        "version": v.version,
                        "checksum": v.checksum,
                        "author_email": v.author_email,
                        "note": v.note,
                        "content": v.content,
                    }
                    for v in versions
                ],
            }
        )
    (backup / "config_retired_backup.json").write_text(
        json.dumps(backed, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Backup config → {backup / 'config_retired_backup.json'}")

    if args.apply:
        for kind, key in targets:
            result = retire_config_key(
                kind, key, purge_versions=not args.keep_versions
            )
            report["retired"].append({"kind": kind, "key": key, **result})
            print(f"  retired {kind}/{key}: {result}")

    # Sync file → DB (fuerza cuerpo de disco cuando difiere; cubre status unknown)
    if not args.skip_sync:
        from src.config_store.paths import (
            AGENT_GUARDRAIL_CLASSES,
            agent_guardrail_key,
            agent_guardrails_dir,
            agent_prompts_dir,
            guardrails_dir,
            path_for,
            skills_dir,
        )
        from src.config_store.service import (
            checksum_content,
            get_active_content,
            save_version,
            strip_header,
        )

        pairs: list[tuple[str, str]] = [("prompt", "sistema")]
        pairs += [("prompt", p.stem) for p in agent_prompts_dir().glob("*.md")]
        pairs += [("guardrail", p.stem) for p in guardrails_dir().glob("g*.md")]
        pairs += [("skill", p.parent.name) for p in skills_dir().glob("*/SKILL.md")]
        root = agent_guardrails_dir()
        if root.is_dir():
            for path in root.glob("*/*.md"):
                if path.stem in AGENT_GUARDRAIL_CLASSES:
                    pairs.append(
                        ("agent_guardrail", agent_guardrail_key(path.parent.name, path.stem))
                    )

        to_sync: list[tuple[str, str]] = []
        for kind, key in pairs:
            fpath = path_for(kind, key)
            if not fpath.is_file():
                continue
            body = strip_header(fpath.read_text(encoding="utf-8")).strip()
            file_cs = checksum_content(body)
            try:
                active = get_active_content(kind, key)
                db_cs = active.get("checksum")
            except Exception:
                db_cs = None
            if db_cs != file_cs:
                to_sync.append((kind, key))
        print(f"Archivos a publicar en DB: {len(to_sync)}")
        if args.apply:
            for kind, key in to_sync:
                try:
                    body = strip_header(path_for(kind, key).read_text(encoding="utf-8")).strip()
                    row = save_version(
                        kind,
                        key,
                        body,
                        author_email=args.author,
                        note="limpieza residuos descartados / desk_policies I/O/T",
                        expected_version=None,
                        write_file=True,
                    )
                    report["synced"].append(
                        {"kind": kind, "key": key, "version": row.get("version")}
                    )
                    print(f"  synced {kind}/{key} → v{row.get('version')}")
                except Exception as exc:  # noqa: BLE001
                    print(f"  FAIL sync {kind}/{key}: {exc}")

    # Demo / residual operational data
    if not args.skip_demo_data:
        url = normalize_database_url(os.environ["DATABASE_URL"])
        eng = create_engine(url, pool_pre_ping=True)
        patterns = {
            "drafts": "tipo ILIKE '%tutela%' OR titulo ILIKE '%tutela%' OR contenido ILIKE '%acción de tutela%'",
            "deadlines": "tipo ILIKE '%tutela%' OR descripcion ILIKE '%tutela%'",
            "chat_sessions": "session_id ILIKE '%tutela%' OR user_id ILIKE '%tutela%'",
        }
        with eng.connect() as conn:
            demo_backup: dict = {}
            for table, where in patterns.items():
                rows = conn.execute(text(f"SELECT * FROM {table} WHERE {where}")).mappings().all()
                demo_backup[table] = [dict(r) for r in rows]
                report["demo_deleted"][table] = {"matched": len(rows)}
                print(f"Demo {table}: {len(rows)} filas")
            (backup / "demo_data_backup.json").write_text(
                json.dumps(demo_backup, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            if args.apply:
                for table, where in patterns.items():
                    result = conn.execute(text(f"DELETE FROM {table} WHERE {where}"))
                    report["demo_deleted"][table]["deleted"] = result.rowcount
                conn.commit()
                print("Demo data eliminada.")

    (backup / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] reporte → {backup / 'report.json'}")
    # sanity: no active tutela keys
    left = [
        f"{a.kind}/{a.key}"
        for a in get_repository().list_config_active()
        if re.search(r"tutela|constitucional", a.key, re.I)
    ]
    if left and args.apply:
        print("WARN: aún activas:", left)
        return 1
    print("OK" if args.apply else "Dry-run listo; reejecute con --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
