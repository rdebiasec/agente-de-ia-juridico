#!/usr/bin/env python3
"""Purga datos fuera de la ventana de retención (Ley 1581).

Uso:
  DATABASE_URL=... python scripts/purge_retention.py --dry-run
  DATABASE_URL=... python scripts/purge_retention.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Purga retención chat/auditoría")
    parser.add_argument("--dry-run", action="store_true", help="Solo cuenta, no borra")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    from src.compliance.retention import purge_expired_data

    summary = purge_expired_data(dry_run=args.dry_run, limit=args.limit)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
