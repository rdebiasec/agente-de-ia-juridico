#!/usr/bin/env python3
"""Smoke LOCAL del triple chat (Fase 5). No toca prod ni Render."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Forzar modo local seguro para el smoke.
os.environ.setdefault("WEB_AUTH_ENABLED", "false")
os.environ.setdefault("IP_ALLOWLIST_ENABLED", "false")
os.environ.setdefault("SITE_PASSWORD", "")

from fastapi.testclient import TestClient

from src.auth.cliente_session import CLIENTE_COOKIE_NAME
from src.auth.gate import COOKIE_NAME as LAWYER_COOKIE
from src.config import get_settings
from src.main import app
from src.storage.memory import InMemoryRepository


def main() -> int:
    get_settings.cache_clear()
    mem = InMemoryRepository()

    import src.services.triple_chat as tc
    import src.storage as storage

    storage.get_repository = lambda: mem  # type: ignore[assignment]
    tc.get_repository = lambda: mem  # type: ignore[assignment]

    client = TestClient(app)
    fails = 0

    def check(name: str, cond: bool) -> None:
        nonlocal fails
        mark = "OK" if cond else "FAIL"
        print(f"[{mark}] {name}")
        if not cond:
            fails += 1

    page = client.get("/cliente")
    check("GET /cliente 200", page.status_code == 200)

    sess = client.get("/cliente/session")
    check("cookies nombres distintos", sess.json().get("cookies_are_separate") is True)
    check(
        "cookie names",
        sess.json().get("cliente_cookie_name") == CLIENTE_COOKIE_NAME
        and sess.json().get("lawyer_cookie_name") == LAWYER_COOKIE,
    )

    post = client.post(
        "/cliente/chat",
        json={
            "message": "Smoke local: estado de mi caso",
            "cliente_session_id": "smoke-local-1",
            "lawyer_session_id": "web:abogada",
        },
    )
    check("POST /cliente/chat 200", post.status_code == 200)
    body = post.json()
    draft_id = body.get("draft_id")
    check("draft_id presente", bool(draft_id))
    check("status_label", bool(body.get("status_label")))
    check("proposed draft no vacío", True)  # draft creado vía enqueue
    check(
        "Set-Cookie cliente",
        CLIENTE_COOKIE_NAME in post.headers.get("set-cookie", "").lower()
        or CLIENTE_COOKIE_NAME in str(client.cookies),
    )

    before = client.get("/cliente/messages", params={"cliente_session_id": "smoke-local-1"})
    before_js = before.json()
    check("sin gerente antes de approve", all(m["role"] == "cliente" for m in before_js.get("messages", [])))
    check("messages en_revision", before_js.get("status") == "en_revision")

    inbox = client.get("/abogado/cliente-inbox?status=proposed")
    check("inbox abogado 200", inbox.status_code == 200)
    drafts = inbox.json().get("drafts") or []
    check("inbox tiene draft", any(d.get("id") == draft_id for d in drafts))
    check("inbox quality_flags key", drafts and "quality_flags" in drafts[0])

    approve = client.post(
        f"/abogado/cliente-drafts/{draft_id}/approve",
        json={"revisor": "abogada", "edited_text": "Respuesta smoke del Gerente."},
    )
    check("approve 200", approve.status_code == 200)

    after = client.get("/cliente/messages", params={"cliente_session_id": "smoke-local-1"})
    after_js = after.json()
    gerente = [m for m in after_js.get("messages", []) if m["role"] == "gerente"]
    check("gerente visible tras approve", bool(gerente))
    check("status respuesta_lista", after_js.get("status") == "respuesta_lista")

    print(f"\nSmoke local: { 'PASS' if fails == 0 else 'FAIL' } ({fails} fallos)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
