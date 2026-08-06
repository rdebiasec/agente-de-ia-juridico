"""Sincronización archivo ↔ DB del config store (drift, import, export, conflicto)."""

from __future__ import annotations

import pytest

from src.config_store import parse_header, save_version
from src.config_store.sync import (
    STATUS_CONFLICT,
    STATUS_DB_AHEAD,
    STATUS_FILE_AHEAD,
    STATUS_IN_SYNC,
    STATUS_NO_DB,
    STATUS_NO_FILE,
    diff_item,
    export_to_file,
    import_to_db,
)
from src.storage import reset_repository

KEY = "g1"
KIND = "guardrail"
AUTHOR = "editor@despacho.com"


@pytest.fixture
def repo_root(tmp_path, monkeypatch):
    """Config store aislado: repositorio en memoria + árbol de archivos temporal."""
    monkeypatch.setenv("DATABASE_URL", "")
    from src.config import get_settings

    get_settings.cache_clear()
    reset_repository()

    from src.config_store import paths

    monkeypatch.setattr(paths, "project_root", lambda: tmp_path)
    (tmp_path / "config" / "guardrails").mkdir(parents=True)
    yield tmp_path

    get_settings.cache_clear()
    reset_repository()


def _write(repo_root, body: str) -> None:
    (repo_root / "config" / "guardrails" / f"{KEY}.md").write_text(body, encoding="utf-8")


def _read(repo_root) -> str:
    return (repo_root / "config" / "guardrails" / f"{KEY}.md").read_text(encoding="utf-8")


def test_file_only_imports_as_v1_and_writes_header(repo_root):
    _write(repo_root, "# No inventar\nRegla original.")

    assert diff_item(KIND, KEY).status == STATUS_NO_DB

    result = import_to_db(diff_item(KIND, KEY), author_email=AUTHOR)
    assert result["version"] == 1

    version, checksum = parse_header(_read(repo_root))
    assert version == 1
    assert checksum == result["checksum"]
    assert diff_item(KIND, KEY).status == STATUS_IN_SYNC


def test_edited_file_is_detected_and_imported_as_next_version(repo_root):
    _write(repo_root, "# No inventar\nRegla original.")
    import_to_db(diff_item(KIND, KEY), author_email=AUTHOR)

    _write(repo_root, "<!-- config-version: 1; checksum: 0000000000000000 -->\n# No inventar\nRegla editada a mano.")

    diff = diff_item(KIND, KEY)
    assert diff.status == STATUS_FILE_AHEAD

    result = import_to_db(diff, author_email=AUTHOR, note="edición manual")
    assert result["version"] == 2

    from src.config_store import get_active_content

    assert "Regla editada a mano." in get_active_content(KIND, KEY)["content"]
    assert diff_item(KIND, KEY).status == STATUS_IN_SYNC


def test_portal_edit_leaves_file_behind_and_export_restores_it(repo_root):
    _write(repo_root, "# No inventar\nRegla original.")
    import_to_db(diff_item(KIND, KEY), author_email=AUTHOR)

    save_version(
        KIND,
        KEY,
        "# No inventar\nRegla desde el portal.",
        author_email="abogada@despacho.com",
        write_file=False,
    )

    diff = diff_item(KIND, KEY)
    assert diff.status == STATUS_DB_AHEAD

    export_to_file(diff)
    contents = _read(repo_root)
    assert "Regla desde el portal." in contents
    assert parse_header(contents)[0] == 2
    assert diff_item(KIND, KEY).status == STATUS_IN_SYNC


def test_both_sides_changed_is_a_conflict_and_import_refuses(repo_root):
    _write(repo_root, "# No inventar\nRegla original.")
    import_to_db(diff_item(KIND, KEY), author_email=AUTHOR)

    save_version(
        KIND,
        KEY,
        "# No inventar\nRegla desde el portal.",
        author_email="abogada@despacho.com",
        write_file=False,
    )
    _write(repo_root, "<!-- config-version: 1; checksum: 0000000000000000 -->\n# No inventar\nRegla editada a mano.")

    diff = diff_item(KIND, KEY)
    assert diff.status == STATUS_CONFLICT

    with pytest.raises(ValueError):
        import_to_db(diff, author_email=AUTHOR)


def test_inflated_header_without_prod_baseline_is_file_ahead(repo_root):
    """Headers de otra DB/rama (vN > activa) no bloquean GitOps archivo → DB."""
    _write(repo_root, "# No inventar\nRegla original.")
    import_to_db(diff_item(KIND, KEY), author_email=AUTHOR)

    _write(
        repo_root,
        "<!-- config-version: 9; checksum: deadbeefdeadbeef -->\n"
        "# No inventar\nRegla desde rama de análisis.",
    )

    diff = diff_item(KIND, KEY)
    assert diff.status == STATUS_FILE_AHEAD
    assert "adelantado" in diff.detail

    result = import_to_db(diff, author_email=AUTHOR, note="A0–A8 gitops")
    assert result["version"] == 2
    assert diff_item(KIND, KEY).status == STATUS_IN_SYNC


def test_missing_file_reports_no_file(repo_root):
    _write(repo_root, "# No inventar\nRegla original.")
    import_to_db(diff_item(KIND, KEY), author_email=AUTHOR)
    (repo_root / "config" / "guardrails" / f"{KEY}.md").unlink()

    diff = diff_item(KIND, KEY)
    assert diff.status == STATUS_NO_FILE

    export_to_file(diff)
    assert "Regla original." in _read(repo_root)
