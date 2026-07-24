#!/usr/bin/env python3
"""Siembra config_versions/config_active desde archivos (idempotente)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed del config store desde filesystem")
    parser.add_argument(
        "--author",
        default="system@seed",
        help="email autor del seed",
    )
    args = parser.parse_args()

    from src.config_store import seed_from_filesystem

    counts = seed_from_filesystem(author_email=args.author)
    print(
        "OK seed:",
        f"prompt={counts['prompt']}",
        f"guardrail={counts['guardrail']}",
        f"skill={counts['skill']}",
        f"skipped={counts['skipped']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
