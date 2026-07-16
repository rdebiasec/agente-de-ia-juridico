#!/usr/bin/env python3
"""Lista o restaura progreso del portal de auditoría desde audit_portal_progress_history.

Uso (producción: External Database URL desde Render → agente-db):
  DATABASE_URL='postgresql+psycopg://...' python scripts/restore_audit_progress.py \\
    --email michele.aguilar@dbx-solutions.com --list

  DATABASE_URL='...' python scripts/restore_audit_progress.py \\
    --email michele.aguilar@dbx-solutions.com --restore
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text

from src.auth.audit_gate import normalize_audit_email
from src.gateway.audit_progress import audit_progress_decision_count


def _load_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _fetch_history(conn, email: str) -> list[dict]:
    rows = conn.execute(
        text(
            """
            SELECT id, email, created_at, payload
            FROM audit_portal_progress_history
            WHERE email = :email
            ORDER BY created_at DESC
            LIMIT 30
            """
        ),
        {"email": email},
    ).fetchall()
    out = []
    for row in rows:
        payload = row.payload or {}
        out.append(
            {
                "id": row.id,
                "email": row.email,
                "created_at": row.created_at,
                "decisions": audit_progress_decision_count(payload),
                "saved_at": (payload or {}).get("savedAt"),
                "payload": payload,
            }
        )
    return out


def _fetch_current(conn, email: str) -> dict | None:
    row = conn.execute(
        text(
            """
            SELECT email, updated_at, payload
            FROM audit_portal_progress
            WHERE email = :email
            """
        ),
        {"email": email},
    ).fetchone()
    if row is None:
        return None
    payload = row.payload or {}
    return {
        "email": row.email,
        "updated_at": row.updated_at,
        "decisions": audit_progress_decision_count(payload),
        "saved_at": payload.get("savedAt"),
        "payload": payload,
    }


def main() -> int:
    _load_env()
    parser = argparse.ArgumentParser(description="Restaurar progreso de auditoría desde historial.")
    parser.add_argument("--email", required=True, help="Correo de la abogada (se normaliza a minúsculas).")
    parser.add_argument("--list", action="store_true", help="Listar fila actual e historial.")
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Restaurar la instantánea del historial con más decisiones (no inventa datos).",
    )
    parser.add_argument(
        "--history-id",
        type=int,
        help="Restaurar un id concreto de audit_portal_progress_history.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Con --restore: muestra qué se restauraría sin escribir en la DB.",
    )
    args = parser.parse_args()
    email = normalize_audit_email(args.email)
    if not args.list and not args.restore:
        parser.error("Indique --list y/o --restore")
    if args.dry_run and not args.restore:
        parser.error("--dry-run requiere --restore")

    db_url = os.environ.get("DATABASE_URL", "").strip()
    if not db_url:
        print("ERROR: configure DATABASE_URL (Render External Database URL en producción).", file=sys.stderr)
        return 1

    engine = create_engine(db_url)
    with engine.begin() as conn:
        current = _fetch_current(conn, email)
        history = _fetch_history(conn, email)

        if args.list:
            print(f"\n=== Progreso actual ({email}) ===")
            if current is None:
                print("(sin fila en audit_portal_progress)")
            else:
                print(
                    f"updated_at={current['updated_at']} decisions={current['decisions']} "
                    f"savedAt={current['saved_at']}"
                )

            print(f"\n=== Historial (hasta 30 entradas) ===")
            if not history:
                print("(sin historial)")
            else:
                for entry in history:
                    print(
                        f"id={entry['id']} created_at={entry['created_at']} "
                        f"decisions={entry['decisions']} savedAt={entry['saved_at']}"
                    )

        if args.restore:
            candidates = [h for h in history if h["decisions"] > 0]
            if args.history_id is not None:
                chosen = next((h for h in history if h["id"] == args.history_id), None)
                if chosen is None:
                    print(f"ERROR: historial id={args.history_id} no encontrado.", file=sys.stderr)
                    return 1
            elif not candidates:
                print("ERROR: no hay instantáneas con decisiones en el historial.", file=sys.stderr)
                return 1
            else:
                chosen = max(candidates, key=lambda h: (h["decisions"], h["created_at"]))

            current_dec = current["decisions"] if current else 0
            if current and current_dec >= chosen["decisions"]:
                print(
                    f"AVISO: el progreso actual ya tiene {current_dec} decisiones; "
                    f"historial elegido tiene {chosen['decisions']}. No se restauró."
                )
                return 0

            if args.dry_run:
                print(
                    f"DRY-RUN: restauraría history id={chosen['id']} "
                    f"({chosen['decisions']} decisiones, created_at={chosen['created_at']}) "
                    f"sobre actual decisions={current_dec}. Sin escritura."
                )
                return 0

            conn.execute(
                text(
                    """
                    INSERT INTO audit_portal_progress (email, payload, created_at, updated_at)
                    VALUES (:email, :payload, NOW(), NOW())
                    ON CONFLICT (email) DO UPDATE
                    SET payload = EXCLUDED.payload, updated_at = NOW()
                    """
                ),
                {"email": email, "payload": chosen["payload"]},
            )
            print(
                f"OK: restaurado desde history id={chosen['id']} "
                f"({chosen['decisions']} decisiones, created_at={chosen['created_at']})"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
