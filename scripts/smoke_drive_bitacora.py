#!/usr/bin/env python3
"""Smoke local: credenciales SA + escritura de casos/_smoke/bitacora.md en Lexiatek.

Uso:
  pip install '.[drive]'
  # .env con GOOGLE_DRIVE_* configurado
  python scripts/smoke_drive_bitacora.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from src.config import get_settings
    from src.services.drive_bitacora import (
        build_drive_service,
        drive_configured,
        ensure_case_folder,
        render_bitacora_md,
        upsert_bitacora_md,
    )
    from src.storage.models import Expediente

    settings = get_settings()
    print("enabled:", settings.google_drive_bitacora_enabled)
    print("root_folder_id:", (settings.google_drive_root_folder_id or "")[:12] + "…")
    print("configured:", drive_configured())

    if not drive_configured():
        print(
            "ERROR: configure GOOGLE_DRIVE_BITACORA_ENABLED, "
            "GOOGLE_DRIVE_ROOT_FOLDER_ID y JSON de SA. "
            "Ver docs/operaciones/GOOGLE_DRIVE_LEXIATEK.md",
            file=sys.stderr,
        )
        return 2

    svc = build_drive_service()
    if svc is None:
        print("ERROR: no se pudo construir el cliente Drive", file=sys.stderr)
        return 2

    # Listar raíz (smoke de permisos)
    root = settings.google_drive_root_folder_id.strip()
    listed = (
        svc.files()
        .list(
            q=f"'{root}' in parents and trashed = false",
            pageSize=10,
            fields="files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="allDrives",
        )
        .execute()
    )
    print("hijos en root:", len(listed.get("files") or []))
    for f in (listed.get("files") or [])[:5]:
        print(" -", f.get("name"), f.get("id"))

    sid = "web:_smoke"
    folder_id = ensure_case_folder(sid, service=svc)
    print("case_folder_id:", folder_id)
    if not folder_id:
        print("ERROR: no se pudo crear/obtener carpeta del caso", file=sys.stderr)
        return 1

    exp = Expediente(
        session_id=sid,
        radicado="SMOKE-000",
        bitacora=[
            {
                "ts": "2026-07-31T00:00:00+00:00",
                "autor": "gerente_caso",
                "tipo": "sintesis",
                "resumen": "Smoke Lexiatek — entrada sintética.",
                "fuentes": ["abogado"],
                "pendientes": [],
                "hallazgos": [],
                "confidencialidad": "normal",
            }
        ],
    )
    content = render_bitacora_md(exp, session_id=sid)
    ok = upsert_bitacora_md(sid, content, service=svc, case_folder_id=folder_id)
    print("upsert_ok:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
