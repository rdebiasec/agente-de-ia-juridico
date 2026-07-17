#!/usr/bin/env python3
"""Smoke HITL: publica 2 borradores de prueba en #revision-abogado (Aprobar / Rechazar).

Uso (con .env o variables de entorno de producción locales):
  .venv/bin/python scripts/smoke_slack_hitl_drafts.py

Luego en Chrome (perfil DBX), en #revision-abogado:
  1) Pulse Aprobar en el primer mensaje
  2) Pulse Rechazar en el segundo
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

    repo = get_repository()
    # id DB: varchar(12)
    d_ok = Draft(
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
    )
    d_no = Draft(
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
    )
    for d in (d_ok, d_no):
        if repo.get_draft(d.id):
            repo.update_draft(d.id, titulo=d.titulo, contenido=d.contenido, estado=d.estado)
        else:
            repo.add_draft(d)

    ts1 = notificar_borrador(d_ok)
    ts2 = notificar_borrador(d_no)
    print(f"Aprobar draft id={d_ok.id} ts={ts1}")
    print(f"Rechazar draft id={d_no.id} ts={ts2}")
    if not ts1 or not ts2:
        print("FAIL: no se pudo publicar en Slack (revise token/canal/invite bot)")
        return 2
    print("OK: mensajes publicados. Complete Aprobar/Rechazar en Chrome DBX.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
