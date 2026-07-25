"""Sincronización archivo ↔ DB del config store.

Permite editar prompts/guardrails/skills en un editor de texto y llevar ese
cambio a Postgres (autoritativo en runtime), o traer a disco lo editado en el
portal de auditoría. El header `<!-- config-version: N; checksum: X -->` de cada
archivo es la marca que permite distinguir quién cambió último y detectar
conflictos en vez de sobrescribir en silencio.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterator

from src.config_store.paths import path_for, relative_path_for
from src.config_store.service import (
    checksum_content,
    list_catalog_items,
    parse_header,
    save_version,
    strip_header,
    with_header,
)
from src.storage import get_repository

logger = logging.getLogger(__name__)

STATUS_IN_SYNC = "in_sync"
STATUS_FILE_AHEAD = "file_ahead"
STATUS_DB_AHEAD = "db_ahead"
STATUS_CONFLICT = "conflict"
STATUS_NO_DB = "no_db"
STATUS_NO_FILE = "no_file"
STATUS_MISSING = "missing"
STATUS_UNKNOWN = "unknown"

#: Estados que `--apply` resuelve escribiendo a la DB.
IMPORTABLE = frozenset({STATUS_FILE_AHEAD, STATUS_NO_DB})
#: Estados que `--export` resuelve escribiendo al archivo.
EXPORTABLE = frozenset({STATUS_DB_AHEAD, STATUS_NO_FILE})
#: Estados que exigen decisión humana.
BLOCKING = frozenset({STATUS_CONFLICT, STATUS_UNKNOWN})


@dataclass(frozen=True)
class ConfigDiff:
    kind: str
    key: str
    path: str
    status: str
    db_version: int
    header_version: int | None
    file_checksum: str | None
    db_checksum: str | None
    detail: str = ""

    @property
    def header_stale(self) -> bool:
        """El cuerpo coincide con la DB pero el header no refleja la versión."""
        return self.status == STATUS_IN_SYNC and self.header_version != self.db_version

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "key": self.key,
            "path": self.path,
            "status": self.status,
            "db_version": self.db_version,
            "header_version": self.header_version,
            "file_checksum": self.file_checksum,
            "db_checksum": self.db_checksum,
            "detail": self.detail,
        }


def _read_file(kind: str, key: str) -> tuple[bool, str, int | None, str | None]:
    path = path_for(kind, key)
    if not path.is_file():
        return False, "", None, None
    raw = path.read_text(encoding="utf-8")
    header_version, header_checksum = parse_header(raw)
    return True, strip_header(raw).strip(), header_version, header_checksum


def diff_item(kind: str, key: str) -> ConfigDiff:
    """Compara el archivo en disco con la versión activa en DB."""
    repo = get_repository()
    active = repo.get_config_active(kind, key)
    db_version = active.active_version if active else 0
    db_checksum = active.checksum if active else None
    exists, body, header_version, _ = _read_file(kind, key)
    file_checksum = checksum_content(body) if exists and body else None

    def build(status: str, detail: str = "") -> ConfigDiff:
        return ConfigDiff(
            kind=kind,
            key=key,
            path=relative_path_for(kind, key),
            status=status,
            db_version=db_version,
            header_version=header_version,
            file_checksum=file_checksum,
            db_checksum=db_checksum,
            detail=detail,
        )

    if not exists or not body:
        if db_version == 0:
            return build(STATUS_MISSING, "sin archivo ni versión en DB")
        return build(STATUS_NO_FILE, "solo existe en DB")
    if db_version == 0:
        return build(STATUS_NO_DB, "solo existe en archivo")
    if file_checksum == db_checksum:
        return build(STATUS_IN_SYNC)

    if header_version is None:
        return build(
            STATUS_UNKNOWN,
            "archivo sin header: no se puede saber si el cambio viene de disco o del portal",
        )
    if header_version == db_version:
        return build(STATUS_FILE_AHEAD, "el archivo fue editado después del último sync")
    if header_version > db_version:
        return build(
            STATUS_UNKNOWN,
            f"header v{header_version} es mayor que la versión activa v{db_version}",
        )

    base = repo.get_config_version(kind, key, header_version)
    if base is not None and checksum_content(strip_header(base.content).strip()) == file_checksum:
        return build(STATUS_DB_AHEAD, "el portal cambió después; el archivo quedó atrás")
    return build(
        STATUS_CONFLICT,
        f"archivo y DB cambiaron desde v{header_version}",
    )


def iter_diffs(kinds: tuple[str, ...] | None = None) -> Iterator[ConfigDiff]:
    """Recorre el catálogo completo (archivos + activos en DB)."""
    catalog = list_catalog_items()
    for kind, items in catalog.items():
        if kinds and kind not in kinds:
            continue
        for item in items:
            yield diff_item(kind, item["key"])


def refresh_header(diff: ConfigDiff) -> bool:
    """Reescribe el header de un archivo ya sincronizado. No toca la DB."""
    if not diff.header_stale or diff.db_checksum is None:
        return False
    exists, body, _, _ = _read_file(diff.kind, diff.key)
    if not exists:
        return False
    path_for(diff.kind, diff.key).write_text(
        with_header(body, version=diff.db_version, checksum=diff.db_checksum),
        encoding="utf-8",
    )
    return True


def import_to_db(diff: ConfigDiff, *, author_email: str, note: str = "") -> dict[str, Any]:
    """Guarda el contenido del archivo como nueva versión activa en DB."""
    if diff.status not in IMPORTABLE:
        raise ValueError(f"{diff.kind}/{diff.key}: estado {diff.status} no es importable")
    exists, body, _, _ = _read_file(diff.kind, diff.key)
    if not exists or not body:
        raise ValueError(f"{diff.kind}/{diff.key}: archivo vacío o ausente")
    return save_version(
        diff.kind,
        diff.key,
        body,
        author_email=author_email,
        note=note or f"sync desde archivo ({diff.status})",
        expected_version=diff.db_version,
        write_file=True,
    )


def export_to_file(diff: ConfigDiff) -> dict[str, Any]:
    """Escribe en disco el contenido activo en DB, con header de versión."""
    if diff.status not in EXPORTABLE and not diff.header_stale:
        raise ValueError(f"{diff.kind}/{diff.key}: estado {diff.status} no es exportable")
    repo = get_repository()
    active = repo.get_config_active(diff.kind, diff.key)
    if active is None:
        raise ValueError(f"{diff.kind}/{diff.key}: sin versión activa en DB")
    row = repo.get_config_version(diff.kind, diff.key, active.active_version)
    if row is None:
        raise ValueError(
            f"{diff.kind}/{diff.key}: falta el contenido de v{active.active_version}"
        )
    body = strip_header(row.content).strip()
    path = path_for(diff.kind, diff.key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        with_header(body, version=row.version, checksum=row.checksum),
        encoding="utf-8",
    )
    return {
        "kind": diff.kind,
        "key": diff.key,
        "version": row.version,
        "checksum": row.checksum,
        "path": relative_path_for(diff.kind, diff.key),
    }


__all__ = [
    "BLOCKING",
    "EXPORTABLE",
    "IMPORTABLE",
    "STATUS_CONFLICT",
    "STATUS_DB_AHEAD",
    "STATUS_FILE_AHEAD",
    "STATUS_IN_SYNC",
    "STATUS_MISSING",
    "STATUS_NO_DB",
    "STATUS_NO_FILE",
    "STATUS_UNKNOWN",
    "ConfigDiff",
    "diff_item",
    "export_to_file",
    "import_to_db",
    "iter_diffs",
    "refresh_header",
]
