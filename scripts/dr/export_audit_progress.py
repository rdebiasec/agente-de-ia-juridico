#!/usr/bin/env python3
"""Exporta progreso de auditoría (actual + historial) a JSON fuera del repo.

Uso:
  .venv/bin/python scripts/dr/export_audit_progress.py
  DATABASE_URL='...' .venv/bin/python scripts/dr/export_audit_progress.py --label prod
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text

from src.gateway.audit_progress import audit_progress_decision_count


def _load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main() -> int:
    _load_env()
    parser = argparse.ArgumentParser(description="Exportar progreso de auditoría a JSON.")
    parser.add_argument("--label", default="local", help="Etiqueta en el nombre del archivo.")
    parser.add_argument(
        "--out-dir",
        default=str(Path.home() / "Backups" / "agente-juridico" / "audit-progress"),
        help="Directorio destino (fuera del repo).",
    )
    args = parser.parse_args()

    db_url = os.environ.get("DATABASE_URL", "").strip()
    if not db_url:
        print("ERROR: configure DATABASE_URL.", file=sys.stderr)
        return 1
    # Render External URL suele ser postgresql://… → forzar driver psycopg3 del proyecto
    if db_url.startswith("postgres://"):
        db_url = "postgresql+psycopg://" + db_url[len("postgres://") :]
    elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        db_url = "postgresql+psycopg://" + db_url[len("postgresql://") :]

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = out_dir / f"audit-progress-{stamp}-{args.label}.json"

    engine = create_engine(db_url)
    with engine.connect() as conn:
        current_rows = conn.execute(
            text("SELECT email, updated_at, payload FROM audit_portal_progress ORDER BY email")
        ).fetchall()
        history_rows = conn.execute(
            text(
                """
                SELECT id, email, created_at, payload
                FROM audit_portal_progress_history
                ORDER BY email, created_at DESC
                """
            )
        ).fetchall()

    current = []
    for row in current_rows:
        payload = row.payload or {}
        current.append(
            {
                "email": row.email,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "decisions": audit_progress_decision_count(payload),
                "payload": payload,
            }
        )

    history = []
    for row in history_rows:
        payload = row.payload or {}
        history.append(
            {
                "id": row.id,
                "email": row.email,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "decisions": audit_progress_decision_count(payload),
                "payload": payload,
            }
        )

    doc = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "label": args.label,
        "current": current,
        "history": history,
        "summary": {
            "users": len(current),
            "history_rows": len(history),
            "users_with_decisions": sum(1 for u in current if u["decisions"] > 0),
            "history_with_decisions": sum(1 for h in history if h["decisions"] > 0),
        },
    }
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {out_path}")
    print(
        f"users={doc['summary']['users']} "
        f"with_decisions={doc['summary']['users_with_decisions']} "
        f"history_with_decisions={doc['summary']['history_with_decisions']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
