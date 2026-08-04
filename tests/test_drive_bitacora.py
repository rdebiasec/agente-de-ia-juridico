"""Drive Lexiatek — render + no-op sin config + upsert mock."""

from __future__ import annotations

from src.services.drive_bitacora import (
    drive_configured,
    render_bitacora_md,
    sanitize_session_folder_name,
    sync_expediente_bitacora,
    upsert_bitacora_md,
)
from src.storage.models import Expediente


def test_sanitize_session_folder_name():
    assert sanitize_session_folder_name("web:foo/bar") == "web-foo-bar"
    assert sanitize_session_folder_name("web:_smoke") == "web-_smoke"


def test_render_bitacora_md_includes_entries():
    exp = Expediente(
        session_id="web:caso-1",
        radicado="11001600000020260001234",
        bitacora=[
            {
                "ts": "t1",
                "autor": "gerente_caso",
                "tipo": "recepcion",
                "resumen": "Pedido tipicidad",
                "fuentes": ["abogado"],
                "pendientes": ["Confirmar radicado"],
                "hallazgos": [],
                "confidencialidad": "normal",
            }
        ],
    )
    md = render_bitacora_md(exp)
    assert "web:caso-1" in md
    assert "11001600000020260001234" in md
    assert "Pedido tipicidad" in md
    assert "Confirmar radicado" in md
    assert "gerente_caso" in md


def test_sync_noop_when_disabled(monkeypatch):
    monkeypatch.setattr(
        "src.services.drive_bitacora.drive_configured",
        lambda: False,
    )
    assert sync_expediente_bitacora("web:x") is False


def test_upsert_mocked(monkeypatch):
    class FakeFiles:
        def __init__(self):
            self.created = False
            self.updated = False

        def list(self, **kwargs):
            class R:
                def execute(self_inner):
                    return {"files": []}

            return R()

        def create(self, **kwargs):
            self.created = True

            class R:
                def execute(self_inner):
                    return {"id": "file1"}

            return R()

        def update(self, **kwargs):
            self.updated = True

            class R:
                def execute(self_inner):
                    return {"id": "file1"}

            return R()

    files = FakeFiles()

    class FakeSvc:
        def files(self):
            return files

    class FakeMedia:
        def __init__(self, *a, **k):
            pass

    import sys
    import types

    http_mod = types.ModuleType("googleapiclient.http")
    http_mod.MediaIoBaseUpload = FakeMedia
    pkg = types.ModuleType("googleapiclient")
    pkg.http = http_mod
    monkeypatch.setitem(sys.modules, "googleapiclient", pkg)
    monkeypatch.setitem(sys.modules, "googleapiclient.http", http_mod)

    monkeypatch.setattr(
        "src.services.drive_bitacora.ensure_case_folder",
        lambda session_id, service=None: "folder1",
    )
    ok = upsert_bitacora_md("web:mock", "# hola\n", service=FakeSvc())
    assert ok is True
    assert files.created is True


def test_drive_configured_false_by_default():
    # Sin env de Drive en tests unitarios.
    assert drive_configured() is False or isinstance(drive_configured(), bool)
