"""Modelos de dominio de la firma (independientes del backend de persistencia)."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


MATERIAS = {"penal"}


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
            return "Expediente sin datos aún; solicite rol de la víctima, partes, radicado y etapa."
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
    tipo: str = "documento"  # memorial, tutela, concepto, correo, estrategia...
    titulo: str = ""
    contenido: str = ""
    materia: str | None = None  # penal
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
    fuente: str = ""  # p.ej. 'proceso-penal-906.md' o 'informe_pericial.pdf'
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


@dataclass
class AuditPortalProgress:
    """Progreso de auditoría del portal (decisiones por correo de la abogada)."""

    email: str
    payload: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class AuditPortalUser:
    email: str
    pin_hash: str
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


@dataclass
class ComplianceConsent:
    subject_key: str
    context: str
    policy_version: str
    privacy_accepted: bool
    sensitive_data_ack: bool
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime = field(default_factory=_now)
    id: int | None = None


@dataclass
class AuditPortalAccessLog:
    action: str
    email: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    detail: str | None = None
    created_at: datetime = field(default_factory=_now)
    id: int | None = None


@dataclass
class ExecutionPlanRecord:
    """Plan de ejecución aprobado por el abogado antes de correr skills."""

    plan_id: str
    session_id: str
    initiator_user_id: str
    channel: str = "web"
    user_message: str = ""
    status: str = "pending_approval"
    payload: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "session_id": self.session_id,
            "initiator_user_id": self.initiator_user_id,
            "channel": self.channel,
            "user_message": self.user_message,
            "status": self.status,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def execution_plan_dashboard_row(record: ExecutionPlanRecord) -> dict:
    """Resumen de un plan para el dashboard del portal de auditoría."""
    payload = record.payload or {}
    steps = payload.get("steps") or []
    agents = payload.get("agents_involved") or []
    stream = payload.get("stream_events") or []
    return {
        "plan_id": record.plan_id,
        "status": record.status,
        "template_kind": payload.get("template_kind") or "generico",
        "objective": (payload.get("objective") or "")[:160],
        "user_message_preview": (record.user_message or "")[:100],
        "session_id": record.session_id,
        "channel": record.channel,
        "steps_count": len(steps),
        "agents_count": len(agents),
        "agents_involved": agents[:4],
        "pattern_reused": bool(payload.get("pattern_reused")),
        "has_result": bool(payload.get("result")),
        "stream_events_count": len(stream),
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
    }


def aggregate_execution_plan_stats(records: list[ExecutionPlanRecord]) -> dict:
    by_status: dict[str, int] = {}
    by_template: dict[str, int] = {}
    for record in records:
        by_status[record.status] = by_status.get(record.status, 0) + 1
        payload = record.payload or {}
        kind = str(payload.get("template_kind") or "generico")
        by_template[kind] = by_template.get(kind, 0) + 1
    recent = [
        execution_plan_dashboard_row(r)
        for r in sorted(records, key=lambda r: r.updated_at, reverse=True)[:25]
    ]
    return {
        "total": len(records),
        "by_status": by_status,
        "by_template": by_template,
        "pending_approval": by_status.get("pending_approval", 0),
        "approved": by_status.get("approved", 0),
        "executing": by_status.get("executing", 0),
        "done": by_status.get("done", 0),
        "failed": by_status.get("failed", 0),
        "rejected": by_status.get("rejected", 0),
        "executed": by_status.get("done", 0) + by_status.get("failed", 0),
        "recent": recent,
        "generated_at": _now().isoformat(),
    }
