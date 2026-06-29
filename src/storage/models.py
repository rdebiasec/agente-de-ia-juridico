"""Modelos de dominio de la firma (independientes del backend de persistencia)."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


MATERIAS = {"civil", "penal", "familia", "societario", "comercial", "laboral", "consumidor"}


@dataclass
class Expediente:
    """Estado mínimo de un caso que guía a los agentes según la etapa."""

    session_id: str
    materia: str | None = None
    tipo_proceso: str | None = None
    rol_despacho: str | None = None  # demandante|demandado|defensa|victima
    radicado: str | None = None
    despacho_judicial: str | None = None
    etapa_actual: str | None = None
    partes: list[dict] = field(default_factory=list)
    terminos: list[dict] = field(default_factory=list)
    actualizado_en: float = field(default_factory=time.time)

    def resumen(self) -> str:
        partes = ["Expediente del caso:"]
        if self.materia:
            partes.append(f"- Materia: {self.materia}")
        if self.tipo_proceso:
            partes.append(f"- Tipo de proceso: {self.tipo_proceso}")
        if self.rol_despacho:
            partes.append(f"- Rol del despacho: {self.rol_despacho}")
        if self.radicado:
            partes.append(f"- Radicado: {self.radicado}")
        if self.etapa_actual:
            partes.append(f"- Etapa actual: {self.etapa_actual}")
        if len(partes) == 1:
            return "Expediente sin datos aún; solicite materia, partes, radicado y etapa."
        return "\n".join(partes)

    def to_dict(self) -> dict:
        return asdict(self)


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


# Estados del flujo de revisión humana (HITL).
ESTADO_PROPUESTO = "propuesto"
ESTADO_EN_REVISION = "en_revision"
ESTADO_APROBADO = "aprobado"
ESTADO_EDITADO = "editado"
ESTADO_RECHAZADO = "rechazado"

ESTADOS_BORRADOR = {
    ESTADO_PROPUESTO,
    ESTADO_EN_REVISION,
    ESTADO_APROBADO,
    ESTADO_EDITADO,
    ESTADO_RECHAZADO,
}
ESTADOS_FINALES = {ESTADO_APROBADO, ESTADO_EDITADO, ESTADO_RECHAZADO}


@dataclass
class Draft:
    """Borrador generado por la IA, sujeto a aprobación del abogado."""

    id: str = field(default_factory=_new_id)
    session_id: str = ""
    tipo: str = "documento"  # memorial, tutela, concepto, contrato, correo, estrategia...
    titulo: str = ""
    contenido: str = ""
    materia: str | None = None  # civil | penal | familia | laboral...
    estado: str = ESTADO_PROPUESTO
    revisor: str | None = None
    comentario: str | None = None
    slack_ts: str | None = None  # timestamp del mensaje de revisión en Slack
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "tipo": self.tipo,
            "titulo": self.titulo,
            "contenido": self.contenido,
            "materia": self.materia,
            "estado": self.estado,
            "revisor": self.revisor,
            "comentario": self.comentario,
            "slack_ts": self.slack_ts,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


SCOPE_KB = "kb"
SCOPE_EXPEDIENTE = "expediente"

# Dimensión de los embeddings (OpenAI text-embedding-3-small / fallback local).
EMBED_DIM = 1536


@dataclass
class DocumentChunk:
    """Fragmento de texto con su embedding para recuperación (RAG)."""

    id: str = field(default_factory=_new_id)
    scope: str = SCOPE_KB  # kb (firma) | expediente (caso)
    expediente_id: str | None = None
    fuente: str = ""  # p.ej. 'proceso-civil-cgp.md' o 'demanda.pdf'
    chunk_text: str = ""
    embedding: list[float] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)
    score: float | None = None  # similitud al recuperar (no se persiste)

    def to_dict(self, *, incluir_embedding: bool = False) -> dict:
        data = {
            "id": self.id,
            "scope": self.scope,
            "expediente_id": self.expediente_id,
            "fuente": self.fuente,
            "chunk_text": self.chunk_text,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "score": self.score,
        }
        if incluir_embedding:
            data["embedding"] = self.embedding
        return data


@dataclass
class Deadline:
    """Término procesal con fecha límite calculada en días hábiles."""

    id: str = field(default_factory=_new_id)
    session_id: str = ""
    descripcion: str = ""
    tipo: str = "termino"  # tutela, traslado, recurso, seguimiento...
    fecha_base: date | None = None
    fecha_limite: date | None = None
    dias_habiles: int | None = None
    estado: str = "pendiente"  # pendiente | cumplido | vencido
    created_at: datetime = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "descripcion": self.descripcion,
            "tipo": self.tipo,
            "fecha_base": self.fecha_base.isoformat() if self.fecha_base else None,
            "fecha_limite": self.fecha_limite.isoformat() if self.fecha_limite else None,
            "dias_habiles": self.dias_habiles,
            "estado": self.estado,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ChatSession:
    """Conversación multi-turno del abogado (mensajes + metadatos de sesión)."""

    session_id: str
    channel: str = "web"
    user_id: str = ""
    messages: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)
    expires_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "channel": self.channel,
            "user_id": self.user_id,
            "messages": self.messages,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "message_count": len(self.messages),
        }


@dataclass
class SessionTrace:
    """Traza enriquecida de un turno (spans, validaciones, completions)."""

    id: str = field(default_factory=lambda: _new_id())
    session_id: str = ""
    trace_id: str = ""
    turn_index: int = 0
    payload: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)

    def to_dict(self) -> dict:
        out = dict(self.payload)
        out.setdefault("trace_id", self.trace_id)
        out.setdefault("session_id", self.session_id)
        out["turn_index"] = self.turn_index
        out["record_id"] = self.id
        out["created_at"] = self.created_at.isoformat()
        return out
