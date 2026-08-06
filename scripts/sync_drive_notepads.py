#!/usr/bin/env python3
"""F5 — Sync / smoke de notepads `{agent_id}.md` hacia Drive Lexiatek.

Sin credenciales: genera MDs locales bajo `tmp/notepads-smoke/` y sale 0.
Con Drive configurado: escribe `casos/<session>/notepads/*.md`.

Uso:
  python scripts/sync_drive_notepads.py
  python scripts/sync_drive_notepads.py --session web:_smoke_notepads
  python scripts/sync_drive_notepads.py --local-only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _synthetic_bitacora(agent_id: str) -> list[dict]:
    return [
        {
            "ts": "2026-08-05T00:00:00+00:00",
            "autor": agent_id,
            "tipo": "analisis",
            "resumen": f"Nota sintética F5 para {agent_id} (sin PII).",
            "fuentes": ["agente/conocimiento/proceso-penal-906.md"],
            "pendientes": ["[PENDIENTE DE VERIFICAR] Confirmar radicado SPOA"],
            "hallazgos": ["Hallazgo piloto notepad"],
            "confidencialidad": "normal",
        }
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--session",
        default="web:_smoke_notepads",
        help="session_id sintético (carpeta Drive)",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="No llamar a Drive; escribir bajo tmp/notepads-smoke/",
    )
    parser.add_argument(
        "--agent",
        default="",
        help="Si se indica, solo ese agent_id",
    )
    args = parser.parse_args()

    from src.services.notepads import (
        NOTEPAD_AGENT_IDS,
        ensure_all_templates,
        render_notepad_md,
    )

    ensure_all_templates()
    agents = [args.agent] if args.agent else list(NOTEPAD_AGENT_IDS)
    bitacora: list[dict] = []
    for aid in agents:
        bitacora.extend(_synthetic_bitacora(aid))
    bitacora.append(
        {
            "ts": "2026-08-05T00:01:00+00:00",
            "autor": "gerente_caso",
            "tipo": "sintesis",
            "resumen": "Síntesis Gerente piloto F5.",
            "fuentes": ["abogado"],
            "pendientes": [],
            "hallazgos": [],
            "confidencialidad": "normal",
        }
    )

    rendered = {
        aid: render_notepad_md(
            aid,
            session_id=args.session,
            bitacora=bitacora,
            eval_or_session=args.session,
        )
        for aid in agents
    }

    if args.local_only:
        out_dir = ROOT / "tmp" / "notepads-smoke" / args.session.replace(":", "-")
        out_dir.mkdir(parents=True, exist_ok=True)
        for aid, content in rendered.items():
            (out_dir / f"{aid}.md").write_text(content, encoding="utf-8")
        print(f"local_ok: {len(rendered)} files → {out_dir}")
        return 0

    from src.services.drive_bitacora import (
        build_drive_service,
        drive_configured,
        ensure_case_folder,
        upsert_notepad_md,
    )

    print("configured:", drive_configured())
    if not drive_configured():
        print(
            "WARN: Drive no configurado — escribiendo local. "
            "Ver docs/operaciones/RUNBOOK_NOTEPADS_DRIVE.md",
            file=sys.stderr,
        )
        out_dir = ROOT / "tmp" / "notepads-smoke" / args.session.replace(":", "-")
        out_dir.mkdir(parents=True, exist_ok=True)
        for aid, content in rendered.items():
            (out_dir / f"{aid}.md").write_text(content, encoding="utf-8")
        print(f"local_fallback: {len(rendered)} → {out_dir}")
        return 0

    svc = build_drive_service()
    if svc is None:
        print("ERROR: no se pudo construir cliente Drive", file=sys.stderr)
        return 2
    folder_id = ensure_case_folder(args.session, service=svc)
    if not folder_id:
        print("ERROR: sin carpeta de caso", file=sys.stderr)
        return 1
    ok = 0
    for aid, content in rendered.items():
        if upsert_notepad_md(
            args.session, aid, content, service=svc, case_folder_id=folder_id
        ):
            ok += 1
            print("upsert:", aid)
    print(f"drive_ok: {ok}/{len(rendered)}")
    return 0 if ok == len(rendered) else 1


if __name__ == "__main__":
    raise SystemExit(main())
