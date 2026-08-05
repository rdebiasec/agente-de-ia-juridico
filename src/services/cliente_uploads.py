"""Adjuntos del canal víctima → disco + expediente del abogado."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from src.storage import get_repository
from src.storage.models import ClientMessage, MSG_VIS_CLIENT

ROOT = Path(__file__).resolve().parents[2]
UPLOAD_ROOT = ROOT / "data" / "cliente_uploads"

ALLOWED_EXT = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
}

DOC_IMAGE_MAX = 10 * 1024 * 1024
VIDEO_MAX = 50 * 1024 * 1024
VIDEO_EXT = {".mp4", ".mov"}

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._\-]+")


class ClienteUploadError(ValueError):
    pass


def _safe_filename(name: str) -> str:
    base = Path(name or "archivo").name
    cleaned = _SAFE_NAME_RE.sub("_", base).strip("._") or "archivo"
    return cleaned[:120]


def _ext(name: str) -> str:
    return Path(name or "").suffix.lower()


def max_bytes_for(ext: str) -> int:
    return VIDEO_MAX if ext in VIDEO_EXT else DOC_IMAGE_MAX


def validate_upload(*, filename: str, size: int, content_type: str | None = None) -> str:
    ext = _ext(filename)
    if ext not in ALLOWED_EXT:
        raise ClienteUploadError(
            "Tipo no permitido. Use PDF, DOC/DOCX, TXT, JPG/PNG/WEBP o MP4/MOV."
        )
    limit = max_bytes_for(ext)
    if size <= 0:
        raise ClienteUploadError("Archivo vacío.")
    if size > limit:
        mb = limit // (1024 * 1024)
        raise ClienteUploadError(f"Archivo demasiado grande (máx {mb} MB para este tipo).")
    return ext


def _lawyer_dir(lawyer_session_id: str) -> Path:
    key = _SAFE_NAME_RE.sub("_", (lawyer_session_id or "web_abogado").replace(":", "_"))
    path = UPLOAD_ROOT / key
    path.mkdir(parents=True, exist_ok=True)
    return path


def store_cliente_upload(
    *,
    thread_id: str,
    lawyer_session_id: str,
    cliente_session_id: str,
    filename: str,
    data: bytes,
    content_type: str | None = None,
) -> dict:
    """Persiste el archivo, deja mensaje visible y anota el expediente."""
    ext = validate_upload(filename=filename, size=len(data), content_type=content_type)
    attachment_id = uuid.uuid4().hex[:12]
    safe = _safe_filename(filename)
    rel_name = f"{attachment_id}_{safe}"
    dest = _lawyer_dir(lawyer_session_id) / rel_name
    dest.write_bytes(data)

    kind = "video" if ext in VIDEO_EXT else ("image" if ext in {".jpg", ".jpeg", ".png", ".webp"} else "document")
    size_mb = len(data) / (1024 * 1024)
    size_label = f"{size_mb:.1f} MB" if size_mb >= 0.1 else f"{len(data)} B"
    label = {"video": "Video", "image": "Foto", "document": "Documento"}[kind]

    repo = get_repository()
    msg = ClientMessage(
        thread_id=thread_id,
        role="cliente",
        content=f"📎 {label} adjunto: {safe} ({size_label})",
        visibility=MSG_VIS_CLIENT,
        meta={
            "kind": "attachment",
            "attachment_id": attachment_id,
            "filename": safe,
            "original_filename": Path(filename or safe).name[:180],
            "content_type": content_type or ALLOWED_EXT.get(ext),
            "size_bytes": len(data),
            "ext": ext,
            "file_kind": kind,
            "rel_path": f"{_SAFE_NAME_RE.sub('_', lawyer_session_id.replace(':', '_'))}/{rel_name}",
        },
    )
    msg = repo.add_client_message(msg)

    exp = repo.get_expediente(lawyer_session_id)
    if exp is None:
        from src.storage.models import Expediente

        exp = Expediente(session_id=lawyer_session_id, lawyer_session_id=lawyer_session_id)
    exp.cliente_session_id = cliente_session_id or exp.cliente_session_id
    exp.lawyer_session_id = lawyer_session_id
    anexos = list((exp.metricas_gerencia or {}).get("anexos_cliente") or [])
    anexo = {
        "id": attachment_id,
        "filename": safe,
        "content_type": content_type or ALLOWED_EXT.get(ext),
        "size_bytes": len(data),
        "file_kind": kind,
        "rel_path": msg.meta["rel_path"],
        "message_id": msg.id,
        "cliente_session_id": cliente_session_id,
    }
    anexos.append(anexo)
    metrics = dict(exp.metricas_gerencia or {})
    metrics["anexos_cliente"] = anexos[-100:]
    exp.metricas_gerencia = metrics
    bit = list(exp.bitacora or [])
    bit.append(
        {
            "autor": "cliente",
            "tipo": "anexo",
            "resumen": f"Adjunto del canal víctima: {safe} ({size_label})",
            "fuentes": ["canal_victima", "cliente_upload"],
            "confidencialidad": "sensible",
            "attachment_id": attachment_id,
        }
    )
    exp.bitacora = bit[-200:]
    repo.save_expediente(exp)

    # Ingesta RAG solo para documentos con texto razonable.
    fragmentos = 0
    if kind == "document" and len(data) <= DOC_IMAGE_MAX:
        try:
            from src.services import rag
            from src.services.documentos import extraer_texto

            texto = extraer_texto(safe, data)
            if texto.strip():
                fragmentos = rag.ingestar_expediente(
                    texto, expediente_id=lawyer_session_id, fuente=f"cliente:{safe}"
                )
        except Exception:
            fragmentos = 0

    return {
        "attachment_id": attachment_id,
        "message_id": msg.id,
        "filename": safe,
        "size_bytes": len(data),
        "file_kind": kind,
        "fragmentos_indexados": fragmentos,
        "content": msg.content,
    }


def resolve_attachment_path(rel_path: str) -> Path | None:
    if not rel_path or ".." in rel_path or rel_path.startswith(("/", "\\")):
        return None
    path = (UPLOAD_ROOT / rel_path).resolve()
    try:
        path.relative_to(UPLOAD_ROOT.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def find_attachment(*, lawyer_session_id: str, attachment_id: str) -> dict | None:
    repo = get_repository()
    exp = repo.get_expediente(lawyer_session_id)
    anexos = list((exp.metricas_gerencia or {}).get("anexos_cliente") or []) if exp else []
    for item in anexos:
        if item.get("id") == attachment_id:
            return item
    return None
