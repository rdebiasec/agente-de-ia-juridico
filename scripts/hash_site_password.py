#!/usr/bin/env python3
"""Genera un hash PBKDF2 para SITE_PASSWORD (usar en .env / Render).

Ejemplo:
  .venv/bin/python scripts/hash_site_password.py 'mi-secreto-largo'
"""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.auth.passwords import hash_password  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Hash SITE_PASSWORD con PBKDF2-SHA256")
    parser.add_argument("password", nargs="?", help="Contraseña en claro (omitir para pedirla)")
    args = parser.parse_args()
    plain = args.password or getpass.getpass("SITE_PASSWORD: ")
    if len(plain) < 12:
        print("Advertencia: use ≥12 caracteres.", file=sys.stderr)
    print(hash_password(plain))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
