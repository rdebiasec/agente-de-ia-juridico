"""Espejo de Expediente.bitacora en Google Drive Shared Drive Lexiatek (.md).

Solo el Gerente dispara el sync (tras append de bitácora). Sin OAuth de abogado:
service account. Fallos se registran y no rompen el chat.
"""

from __future__ import annotations

import io
import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DRIVE_SCOPE = ("https://www.googleapis.com/auth/drive",)
_CASOS_FOLDER_NAME = "casos"
_BITACORA_FILENAME = "bitacora.md"
_FOLDER_MIME = "application/vnd.google-apps.folder"
_MD_MIME = "text/markdown"


def sanitize_session_folder_name(session_id: str) -> str:
    """web:foo → web-foo (seguro para nombres en Drive)."""
    raw = (session_id or "").strip() or "_sin_sesion"
    cleaned = re.sub(r"[^\w.\-]+", "-", raw, flags=re.UNICODE)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-._")
    return (cleaned or "_caso")[:120]


def drive_configured() -> bool:
    from src.config import get_settings

    settings = get_settings()
    if not settings.google_drive_bitacora_enabled:
        return False
    if not (settings.google_drive_root_folder_id or "").strip():
        return False
    path = _credentials_path()
    return bool(path and Path(path).is_file())


def _credentials_path() -> str | None:
    from src.config import get_settings

    settings = get_settings()
    explicit = (settings.google_drive_service_account_file or "").strip()
    if explicit:
        return explicit
    adc = (os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
    return adc or None


def build_drive_service():
    """Construye el cliente Drive v3 o None si faltan deps/credenciales."""
    path = _credentials_path()
    if not path or not Path(path).is_file():
        logger.warning("Drive Lexiatek: falta JSON de service account")
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        logger.warning(
            "Drive Lexiatek: instale dependencias con pip install '.[drive]'"
        )
        return None

    creds = service_account.Credentials.from_service_account_file(
        path, scopes=list(_DRIVE_SCOPE)
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def render_bitacora_md(expediente: Any, *, session_id: str | None = None) -> str:
    """Genera markdown legible desde el expediente (solo bitácora normalizada)."""
    sid = session_id or getattr(expediente, "session_id", "") or ""
    radicado = getattr(expediente, "radicado", None) or ""
    etapa = getattr(expediente, "etapa_actual", None) or ""
    entries = list(getattr(expediente, "bitacora", None) or [])

    lines = [
        "# Bitácora del caso — Lexiatek",
        "",
        f"- **session_id:** `{sid}`",
    ]
    if radicado:
        lines.append(f"- **radicado:** {radicado}")
    if etapa:
        lines.append(f"- **etapa:** {etapa}")
    lines.extend(
        [
            "",
            "> Espejo de lectura. Fuente de verdad: Postgres (`Expediente.bitacora`).",
            "> No usar datos reales de víctimas en local sin DPA Google.",
            "",
            "## Entradas",
            "",
        ]
    )
    if not entries:
        lines.append("_Sin entradas aún._")
        lines.append("")
        return "\n".join(lines)

    for i, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            continue
        ts = entry.get("ts") or ""
        autor = entry.get("autor") or ""
        tipo = entry.get("tipo") or ""
        resumen = (entry.get("resumen") or "").strip()
        pendientes = entry.get("pendientes") or []
        hallazgos = entry.get("hallazgos") or []
        fuentes = entry.get("fuentes") or []
        conf = entry.get("confidencialidad") or "normal"
        lines.append(f"### {i}. [{tipo}] {autor}")
        lines.append(f"- **ts:** {ts}")
        lines.append(f"- **confidencialidad:** {conf}")
        if fuentes:
            lines.append(f"- **fuentes:** {', '.join(str(f) for f in fuentes)}")
        if resumen:
            lines.append(f"- **resumen:** {resumen}")
        if hallazgos:
            lines.append("- **hallazgos:**")
            for h in hallazgos:
                lines.append(f"  - {h}")
        if pendientes:
            lines.append("- **pendientes:**")
            for p in pendientes:
                lines.append(f"  - {p}")
        lines.append("")
    return "\n".join(lines)


def _list_children(
    service,
    *,
    parent_id: str,
    name: str,
    mime_type: str | None = None,
) -> str | None:
    safe_name = name.replace("'", "\\'")
    q = f"'{parent_id}' in parents and name = '{safe_name}' and trashed = false"
    if mime_type:
        q += f" and mimeType = '{mime_type}'"
    resp = (
        service.files()
        .list(
            q=q,
            spaces="drive",
            fields="files(id, name)",
            pageSize=5,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="allDrives",
        )
        .execute()
    )
    files = resp.get("files") or []
    if not files:
        return None
    return files[0]["id"]


def _create_folder(service, *, parent_id: str, name: str) -> str:
    meta = {
        "name": name,
        "mimeType": _FOLDER_MIME,
        "parents": [parent_id],
    }
    created = (
        service.files()
        .create(body=meta, fields="id", supportsAllDrives=True)
        .execute()
    )
    return created["id"]


def ensure_child_folder(service, *, parent_id: str, name: str) -> str:
    existing = _list_children(
        service, parent_id=parent_id, name=name, mime_type=_FOLDER_MIME
    )
    if existing:
        return existing
    return _create_folder(service, parent_id=parent_id, name=name)


def ensure_case_folder(session_id: str, *, service=None) -> str | None:
    """Asegura Lexiatek/casos/<session>/ y devuelve folder_id."""
    from src.config import get_settings

    settings = get_settings()
    root = (settings.google_drive_root_folder_id or "").strip()
    if not root:
        return None
    svc = service or build_drive_service()
    if svc is None:
        return None
    # Si ROOT apunta a Lexiatek, creamos/usamos `casos/`. Si ya es `casos/`,
    # detectamos por nombre de un hijo o simplemente usamos root como parent de casos.
    # Convención: ROOT = Lexiatek o la carpeta `casos`.
    # Intentamos encontrar/crear `casos` bajo root; si falla create (root ya es casos),
    # usamos root directamente cuando el nombre sanitizado no choca.
    casos_id = _list_children(
        svc, parent_id=root, name=_CASOS_FOLDER_NAME, mime_type=_FOLDER_MIME
    )
    if casos_id is None:
        # ¿ROOT ya es la carpeta casos? Crear sesión directamente bajo root.
        # Heurística: si podemos crear `casos` bajo root, lo hacemos; si el
        # operador puso el ID de `casos`, listar hijos y crear session ahí.
        try:
            casos_id = _create_folder(svc, parent_id=root, name=_CASOS_FOLDER_NAME)
        except Exception:
            logger.info(
                "Drive Lexiatek: no se creó 'casos/' bajo root; se usa root como casos/"
            )
            casos_id = root
    folder_name = sanitize_session_folder_name(session_id)
    return ensure_child_folder(svc, parent_id=casos_id, name=folder_name)


def upsert_bitacora_md(
    session_id: str,
    content: str,
    *,
    service=None,
    case_folder_id: str | None = None,
) -> bool:
    """Crea o actualiza bitacora.md en la carpeta del caso."""
    try:
        from googleapiclient.http import MediaIoBaseUpload
    except ImportError:
        logger.warning("Drive Lexiatek: falta googleapiclient")
        return False

    svc = service or build_drive_service()
    if svc is None:
        return False
    folder_id = case_folder_id or ensure_case_folder(session_id, service=svc)
    if not folder_id:
        return False

    file_id = _list_children(
        svc, parent_id=folder_id, name=_BITACORA_FILENAME, mime_type=None
    )
    media = MediaIoBaseUpload(
        io.BytesIO((content or "").encode("utf-8")),
        mimetype=_MD_MIME,
        resumable=False,
    )
    if file_id:
        svc.files().update(
            fileId=file_id,
            media_body=media,
            supportsAllDrives=True,
        ).execute()
    else:
        meta = {
            "name": _BITACORA_FILENAME,
            "parents": [folder_id],
            "mimeType": _MD_MIME,
        }
        svc.files().create(
            body=meta,
            media_body=media,
            fields="id",
            supportsAllDrives=True,
        ).execute()
    return True


def sync_expediente_bitacora(session_id: str) -> bool:
    """Best-effort: reescribe bitacora.md desde el expediente. Nunca raise."""
    sid = (session_id or "").strip()
    if not sid:
        return False
    if not drive_configured():
        return False
    try:
        from src.gateway.expediente import expediente_store

        exp = expediente_store.get(sid)
        if exp is None:
            logger.debug("Drive Lexiatek: sin expediente para %s", sid)
            return False
        content = render_bitacora_md(exp, session_id=sid)
        ok = upsert_bitacora_md(sid, content)
        if ok:
            logger.info("Drive Lexiatek: sync OK session=%s", sid)
        else:
            logger.warning("Drive Lexiatek: sync falló session=%s", sid)
        return ok
    except Exception:
        logger.exception("Drive Lexiatek: error sync session=%s", sid)
        return False
