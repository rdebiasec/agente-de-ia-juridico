#!/usr/bin/env python3
"""Smoke HITL: publica 3 borradores de prueba en #revision-abogado.

Uso (con .env o variables de entorno de producción locales):
  .venv/bin/python scripts/smoke_slack_hitl_drafts.py

Luego en Slack, en #revision-abogado:
  1) Pulse Aprobar en el primer mensaje
  2) Pulse Editar en el segundo (modal → Guarde)
  3) Pulse Rechazar en el tercero
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import get_settings
from src.hitl.slack_review import notificar_borrador, slack_habilitado
from src.storage import get_repository
from src.storage.models import ESTADO_EN_REVISION, Draft


def main() -> int:
    settings = get_settings()
    if not slack_habilitado():
        print("FAIL: SLACK_BOT_TOKEN no configurado")
        return 1
    print(f"Canal: {settings.slack_review_channel}")
    allow = settings.slack_approver_allowlist()
    if allow:
        print(f"Allowlist activa: {sorted(allow)}")
    else:
        print("Allowlist vacía (cualquier usuario del canal puede revisar)")

    repo = get_repository()
    drafts = [
        Draft(
            id="smk-apr-001",
            session_id="slack:smoke",
            tipo="memorial",
            titulo="[SMOKE] Borrador para APROBAR",
            contenido=(
                "Texto de prueba HITL. Pulse **Aprobar** en Slack.\n"
                "Borrador informativo — requiere revisión del abogado."
            ),
            estado=ESTADO_EN_REVISION,
            materia="penal",
        ),
        Draft(
            id="smk-edt-001",
            session_id="slack:smoke",
            tipo="memorial",
            titulo="[SMOKE] Borrador para EDITAR",
            contenido=(
                "Texto de prueba HITL. Pulse **Editar** en Slack y guarde el modal.\n"
                "Borrador informativo — requiere revisión del abogado."
            ),
            estado=ESTADO_EN_REVISION,
            materia="penal",
        ),
        Draft(
            id="smk-rej-001",
            session_id="slack:smoke",
            tipo="memorial",
            titulo="[SMOKE] Borrador para RECHAZAR",
            contenido=(
                "Texto de prueba HITL. Pulse **Rechazar** en Slack.\n"
                "Borrador informativo — requiere revisión del abogado."
            ),
            estado=ESTADO_EN_REVISION,
            materia="penal",
        ),
    ]
    for d in drafts:
        if repo.get_draft(d.id):
            repo.update_draft(d.id, titulo=d.titulo, contenido=d.contenido, estado=d.estado)
        else:
            repo.add_draft(d)

    results = []
    for d in drafts:
        ts = notificar_borrador(d)
        results.append((d.id, d.titulo, ts))
        print(f"{d.titulo} id={d.id} ts={ts}")

    if any(ts is None for _, _, ts in results):
        print("FAIL: no se pudo publicar en Slack (revise token/canal/invite bot)")
        return 2
    print("OK: mensajes publicados. Complete Aprobar / Editar / Rechazar en Slack.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
