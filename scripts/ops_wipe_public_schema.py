#!/usr/bin/env python3
"""Wipe irreversible del schema public (arranque de cero).

Uso (solo CI / ops explícito):
  DATABASE_URL=... .venv/bin/python scripts/ops_wipe_public_schema.py --confirm WIPE
"""

from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", required=True, help='Debe ser exactamente "WIPE"')
    args = parser.parse_args()
    if args.confirm != "WIPE":
        print("Abortado: --confirm debe ser WIPE", file=sys.stderr)
        return 2

    url = (os.environ.get("DATABASE_URL") or "").strip()
    if not url:
        print("Abortado: falta DATABASE_URL", file=sys.stderr)
        return 2

    from sqlalchemy import create_engine, text

    from src.storage.sql import normalize_database_url

    engine = create_engine(normalize_database_url(url), isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
    print("OK: schema public recreado (vacío)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
