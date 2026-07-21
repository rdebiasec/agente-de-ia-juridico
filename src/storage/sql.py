"""Backend SQLAlchemy/Postgres + pgvector (paridad dev==prod vía Docker o Render).

Se activa cuando `DATABASE_URL` está configurado. Incluye la tabla de
fragmentos con embeddings para RAG (búsqueda por similitud coseno).
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, Date, DateTime, Float, String, Text, create_engine, delete, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from src.storage.models import (
    AuditPortalAccessLog,
    AuditPortalProgress,
    AuditPortalUser,
    ChatSession,
    ComplianceConsent,
    Deadline,
    DocumentChunk,
    Draft,
    EMBED_DIM,
    ExecutionPlanRecord,
    Expediente,
    SessionTrace,
)


def normalize_database_url(url: str) -> str:
    """Render entrega `postgres://`; SQLAlchemy + psycopg3 requiere `postgresql+psycopg://`."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Base(DeclarativeBase):
    pass


class DraftRow(Base):
    __tablename__ = "drafts"

    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(120), index=True, default="")
    tipo: Mapped[str] = mapped_column(String(40), default="documento")
    titulo: Mapped[str] = mapped_column(String(300), default="")
    contenido: Mapped[str] = mapped_column(Text, default="")
    materia: Mapped[str | None] = mapped_column(String(40), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), index=True, default="propuesto")
    revisor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    slack_ts: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DocumentChunkRow(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    scope: Mapped[str] = mapped_column(String(20), index=True, default="kb")
    expediente_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    fuente: Mapped[str] = mapped_column(Text, default="")
    chunk_text: Mapped[str] = mapped_column(Text, default="")
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
    chunk_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExpedienteRow(Base):
    __tablename__ = "expedientes"

    session_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    materia: Mapped[str | None] = mapped_column(String(40), nullable=True)
    tipo_proceso: Mapped[str | None] = mapped_column(String(60), nullable=True)
    rol_despacho: Mapped[str | None] = mapped_column(String(40), nullable=True)
    radicado: Mapped[str | None] = mapped_column(String(120), nullable=True)
    despacho_judicial: Mapped[str | None] = mapped_column(String(200), nullable=True)
    etapa_actual: Mapped[str | None] = mapped_column(String(120), nullable=True)
    partes: Mapped[list] = mapped_column(JSON, default=list)
    terminos: Mapped[list] = mapped_column(JSON, default=list)
    involucra_menor: Mapped[bool] = mapped_column(Boolean, default=False)
    datos_sensibles: Mapped[bool] = mapped_column(Boolean, default=False)
    actualizado_en: Mapped[float] = mapped_column(Float, default=0.0)


class DeadlineRow(Base):
    __tablename__ = "deadlines"

    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(120), index=True, default="")
    descripcion: Mapped[str] = mapped_column(Text, default="")
    tipo: Mapped[str] = mapped_column(String(40), default="termino")
    fecha_base: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_limite: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    dias_habiles: Mapped[int | None] = mapped_column(nullable=True)
    estado: Mapped[str] = mapped_column(String(20), index=True, default="pendiente")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ChatSessionRow(Base):
    __tablename__ = "chat_sessions"

    session_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    channel: Mapped[str] = mapped_column(String(20), default="web")
    user_id: Mapped[str] = mapped_column(String(120), default="", index=True)
    messages: Mapped[list] = mapped_column(JSON, default=list)
    session_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SessionTraceRow(Base):
    __tablename__ = "session_traces"

    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(120), index=True)
    trace_id: Mapped[str] = mapped_column(String(40), index=True)
    turn_index: Mapped[int] = mapped_column(default=0)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditPortalProgressRow(Base):
    __tablename__ = "audit_portal_progress"

    email: Mapped[str] = mapped_column(Text, primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditPortalUserRow(Base):
    __tablename__ = "audit_portal_user"

    email: Mapped[str] = mapped_column(Text, primary_key=True)
    pin_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ComplianceConsentRow(Base):
    __tablename__ = "compliance_consent"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_key: Mapped[str] = mapped_column(Text, index=True)
    context: Mapped[str] = mapped_column(Text)
    policy_version: Mapped[str] = mapped_column(Text)
    privacy_accepted: Mapped[bool] = mapped_column(default=True)
    sensitive_data_ack: Mapped[bool] = mapped_column(default=False)
    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditPortalAccessLogRow(Base):
    __tablename__ = "audit_portal_access_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(Text, index=True, nullable=True)
    action: Mapped[str] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditPortalProgressHistoryRow(Base):
    __tablename__ = "audit_portal_progress_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(Text, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExecutionPlanRow(Base):
    __tablename__ = "execution_plans"

    plan_id: Mapped[str] = mapped_column(Text, primary_key=True)
    session_id: Mapped[str] = mapped_column(Text, index=True)
    initiator_user_id: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(Text, default="web")
    user_message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def _to_execution_plan(row: ExecutionPlanRow) -> ExecutionPlanRecord:
    return ExecutionPlanRecord(
        plan_id=row.plan_id,
        session_id=row.session_id,
        initiator_user_id=row.initiator_user_id,
        channel=row.channel,
        user_message=row.user_message,
        status=row.status,
        payload=row.payload or {},
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_draft(row: DraftRow) -> Draft:
    from src.compliance.crypto_at_rest import decrypt_text

    return Draft(
        id=row.id,
        session_id=row.session_id,
        tipo=row.tipo,
        titulo=row.titulo,
        contenido=decrypt_text(row.contenido),
        materia=row.materia,
        estado=row.estado,
        revisor=row.revisor,
        comentario=row.comentario,
        slack_ts=row.slack_ts,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_chunk(row: DocumentChunkRow, score: float | None = None) -> DocumentChunk:
    return DocumentChunk(
        id=row.id,
        scope=row.scope,
        expediente_id=row.expediente_id,
        fuente=row.fuente,
        chunk_text=row.chunk_text,
        embedding=[],
        metadata=row.chunk_metadata or {},
        created_at=row.created_at,
        score=score,
    )


def _to_expediente(row: ExpedienteRow) -> Expediente:
    return Expediente(
        session_id=row.session_id,
        materia=row.materia,
        tipo_proceso=row.tipo_proceso,
        rol_despacho=row.rol_despacho,
        radicado=row.radicado,
        despacho_judicial=row.despacho_judicial,
        etapa_actual=row.etapa_actual,
        partes=row.partes or [],
        terminos=row.terminos or [],
        involucra_menor=bool(getattr(row, "involucra_menor", False)),
        datos_sensibles=bool(getattr(row, "datos_sensibles", False)),
        actualizado_en=row.actualizado_en or 0.0,
    )


def _to_chat_session(row: ChatSessionRow) -> ChatSession:
    from src.compliance.crypto_at_rest import decrypt_messages

    return ChatSession(
        session_id=row.session_id,
        channel=row.channel,
        user_id=row.user_id,
        messages=decrypt_messages(row.messages or []),
        metadata=row.session_metadata or {},
        created_at=row.created_at,
        updated_at=row.updated_at,
        expires_at=row.expires_at,
    )


def _to_session_trace(row: SessionTraceRow) -> SessionTrace:
    return SessionTrace(
        id=row.id,
        session_id=row.session_id,
        trace_id=row.trace_id,
        turn_index=row.turn_index,
        payload=row.payload or {},
        created_at=row.created_at,
    )


def _to_deadline(row: DeadlineRow) -> Deadline:
    return Deadline(
        id=row.id,
        session_id=row.session_id,
        descripcion=row.descripcion,
        tipo=row.tipo,
        fecha_base=row.fecha_base,
        fecha_limite=row.fecha_limite,
        dias_habiles=row.dias_habiles,
        estado=row.estado,
        created_at=row.created_at,
    )


class SqlRepository:
    def __init__(self, database_url: str, *, create_all: bool = False) -> None:
        self.engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
        self._session: sessionmaker[Session] = sessionmaker(bind=self.engine)
        if create_all:
            self.ensure_schema()

    def ensure_schema(self) -> None:
        """Crea extensión y tablas (fallback si no se usan migraciones Alembic)."""
        with self.engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(self.engine)

    # --- Borradores ---
    def add_draft(self, draft: Draft) -> Draft:
        from src.compliance.crypto_at_rest import encrypt_text

        with self._session() as s:
            row = DraftRow(
                id=draft.id,
                session_id=draft.session_id,
                tipo=draft.tipo,
                titulo=draft.titulo,
                contenido=encrypt_text(draft.contenido),
                materia=draft.materia,
                estado=draft.estado,
                revisor=draft.revisor,
                comentario=draft.comentario,
                slack_ts=draft.slack_ts,
                created_at=draft.created_at,
                updated_at=draft.updated_at,
            )
            s.add(row)
            s.commit()
        return draft

    def get_draft(self, draft_id: str) -> Draft | None:
        with self._session() as s:
            row = s.get(DraftRow, draft_id)
            return _to_draft(row) if row else None

    def list_drafts(
        self, *, estado: str | None = None, session_id: str | None = None
    ) -> list[Draft]:
        with self._session() as s:
            stmt = select(DraftRow)
            if estado is not None:
                stmt = stmt.where(DraftRow.estado == estado)
            if session_id is not None:
                stmt = stmt.where(DraftRow.session_id == session_id)
            stmt = stmt.order_by(DraftRow.created_at.desc())
            return [_to_draft(r) for r in s.scalars(stmt).all()]

    def update_draft(self, draft_id: str, **changes) -> Draft | None:
        from src.compliance.crypto_at_rest import encrypt_text

        with self._session() as s:
            row = s.get(DraftRow, draft_id)
            if row is None:
                return None
            for key, value in changes.items():
                if not hasattr(row, key):
                    continue
                if key == "contenido" and isinstance(value, str):
                    setattr(row, key, encrypt_text(value))
                else:
                    setattr(row, key, value)
            row.updated_at = datetime.now(timezone.utc)
            s.commit()
            return _to_draft(row)

    def delete_drafts_for_session(self, session_id: str) -> int:
        with self._session() as s:
            result = s.execute(delete(DraftRow).where(DraftRow.session_id == session_id))
            s.commit()
            return int(result.rowcount or 0)

    def delete_chat_session(self, session_id: str) -> bool:
        with self._session() as s:
            row = s.get(ChatSessionRow, session_id)
            if row is None:
                return False
            s.delete(row)
            s.commit()
            return True

    def delete_expediente(self, session_id: str) -> bool:
        with self._session() as s:
            row = s.get(ExpedienteRow, session_id)
            if row is None:
                return False
            s.delete(row)
            s.commit()
            return True

    def delete_execution_plans_for_user(self, user_id: str) -> int:
        with self._session() as s:
            result = s.execute(
                delete(ExecutionPlanRow).where(ExecutionPlanRow.initiator_user_id == user_id)
            )
            s.commit()
            return int(result.rowcount or 0)

    def list_stale_chat_sessions(self, *, older_than: datetime, limit: int = 500) -> list[ChatSession]:
        with self._session() as s:
            stmt = (
                select(ChatSessionRow)
                .where(ChatSessionRow.updated_at < older_than)
                .order_by(ChatSessionRow.updated_at.asc())
                .limit(limit)
            )
            return [_to_chat_session(r) for r in s.scalars(stmt).all()]

    def list_stale_audit_progress_emails(self, *, older_than: datetime, limit: int = 500) -> list[str]:
        with self._session() as s:
            stmt = (
                select(AuditPortalProgressRow.email)
                .where(AuditPortalProgressRow.updated_at < older_than)
                .order_by(AuditPortalProgressRow.updated_at.asc())
                .limit(limit)
            )
            return [str(e) for e in s.scalars(stmt).all()]

    # --- Términos ---
    def add_deadline(self, deadline: Deadline) -> Deadline:
        with self._session() as s:
            row = DeadlineRow(
                id=deadline.id,
                session_id=deadline.session_id,
                descripcion=deadline.descripcion,
                tipo=deadline.tipo,
                fecha_base=deadline.fecha_base,
                fecha_limite=deadline.fecha_limite,
                dias_habiles=deadline.dias_habiles,
                estado=deadline.estado,
                created_at=deadline.created_at,
            )
            s.add(row)
            s.commit()
        return deadline

    def list_deadlines(
        self, *, session_id: str | None = None, solo_pendientes: bool = False
    ) -> list[Deadline]:
        with self._session() as s:
            stmt = select(DeadlineRow)
            if session_id is not None:
                stmt = stmt.where(DeadlineRow.session_id == session_id)
            if solo_pendientes:
                stmt = stmt.where(DeadlineRow.estado == "pendiente")
            stmt = stmt.order_by(DeadlineRow.fecha_limite.asc())
            return [_to_deadline(r) for r in s.scalars(stmt).all()]

    def update_deadline(self, deadline_id: str, **changes) -> Deadline | None:
        with self._session() as s:
            row = s.get(DeadlineRow, deadline_id)
            if row is None:
                return None
            for key, value in changes.items():
                if hasattr(row, key):
                    setattr(row, key, value)
            s.commit()
            return _to_deadline(row)

    # --- RAG ---
    def add_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        self.add_chunks([chunk])
        return chunk

    def add_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0
        with self._session() as s:
            for chunk in chunks:
                s.add(
                    DocumentChunkRow(
                        id=chunk.id,
                        scope=chunk.scope,
                        expediente_id=chunk.expediente_id,
                        fuente=chunk.fuente,
                        chunk_text=chunk.chunk_text,
                        embedding=chunk.embedding,
                        chunk_metadata=chunk.metadata,
                        created_at=chunk.created_at,
                    )
                )
            s.commit()
        return len(chunks)

    def buscar_similares(
        self,
        embedding: list[float],
        *,
        expediente_id: str | None = None,
        incluir_kb: bool = True,
        k: int = 5,
    ) -> list[DocumentChunk]:
        from sqlalchemy import or_

        with self._session() as s:
            distancia = DocumentChunkRow.embedding.cosine_distance(embedding).label("distancia")
            stmt = select(DocumentChunkRow, distancia)

            condiciones = []
            if incluir_kb:
                condiciones.append(DocumentChunkRow.scope == "kb")
            if expediente_id is not None:
                condiciones.append(DocumentChunkRow.expediente_id == expediente_id)
            if condiciones:
                stmt = stmt.where(or_(*condiciones))
            else:
                return []

            stmt = stmt.order_by(distancia.asc()).limit(k)
            resultados = []
            for row, dist in s.execute(stmt).all():
                # score de similitud coseno = 1 - distancia
                resultados.append(_to_chunk(row, score=1.0 - float(dist)))
            return resultados

    def contar_chunks(
        self, *, scope: str | None = None, expediente_id: str | None = None, fuente: str | None = None
    ) -> int:
        from sqlalchemy import func

        with self._session() as s:
            stmt = select(func.count()).select_from(DocumentChunkRow)
            if scope is not None:
                stmt = stmt.where(DocumentChunkRow.scope == scope)
            if expediente_id is not None:
                stmt = stmt.where(DocumentChunkRow.expediente_id == expediente_id)
            if fuente is not None:
                stmt = stmt.where(DocumentChunkRow.fuente == fuente)
            return int(s.scalar(stmt) or 0)

    # --- Expediente ---
    def get_expediente(self, session_id: str) -> Expediente | None:
        with self._session() as s:
            row = s.get(ExpedienteRow, session_id)
            return _to_expediente(row) if row else None

    def save_expediente(self, expediente: Expediente) -> Expediente:
        with self._session() as s:
            row = s.get(ExpedienteRow, expediente.session_id)
            if row is None:
                row = ExpedienteRow(session_id=expediente.session_id)
                s.add(row)
            row.materia = expediente.materia
            row.tipo_proceso = expediente.tipo_proceso
            row.rol_despacho = expediente.rol_despacho
            row.radicado = expediente.radicado
            row.despacho_judicial = expediente.despacho_judicial
            row.etapa_actual = expediente.etapa_actual
            row.partes = expediente.partes
            row.terminos = expediente.terminos
            row.involucra_menor = bool(expediente.involucra_menor)
            row.datos_sensibles = bool(expediente.datos_sensibles)
            row.actualizado_en = expediente.actualizado_en
            s.commit()
        return expediente

    # --- Conversación y trazas ---
    def get_chat_session(self, session_id: str) -> ChatSession | None:
        with self._session() as s:
            row = s.get(ChatSessionRow, session_id)
            return _to_chat_session(row) if row else None

    def save_chat_session(self, session: ChatSession) -> ChatSession:
        from src.compliance.crypto_at_rest import encrypt_messages

        with self._session() as s:
            row = s.get(ChatSessionRow, session.session_id)
            if row is None:
                row = ChatSessionRow(session_id=session.session_id)
                s.add(row)
            row.channel = session.channel
            row.user_id = session.user_id
            row.messages = encrypt_messages(session.messages)
            row.session_metadata = session.metadata
            row.created_at = session.created_at
            row.updated_at = session.updated_at
            row.expires_at = session.expires_at
            s.commit()
            return _to_chat_session(row)

    def append_chat_message(
        self, session_id: str, *, channel: str, user_id: str, role: str, content: str, max_messages: int
    ) -> ChatSession:
        import time

        now = datetime.now(timezone.utc)
        with self._session() as s:
            row = s.get(ChatSessionRow, session_id)
            if row is None:
                row = ChatSessionRow(
                    session_id=session_id,
                    channel=channel,
                    user_id=user_id,
                    messages=[],
                    session_metadata={},
                    created_at=now,
                    updated_at=now,
                )
                s.add(row)
            from src.compliance.crypto_at_rest import encrypt_text

            messages = list(row.messages or [])
            messages.append({"role": role, "content": encrypt_text(content), "ts": time.time()})
            if len(messages) > max_messages:
                messages = messages[-max_messages:]
            row.messages = messages
            row.channel = channel
            row.user_id = user_id
            row.updated_at = now
            s.commit()
            return _to_chat_session(row)

    def add_session_trace(self, trace: SessionTrace) -> SessionTrace:
        with self._session() as s:
            row = SessionTraceRow(
                id=trace.id,
                session_id=trace.session_id,
                trace_id=trace.trace_id,
                turn_index=trace.turn_index,
                payload=trace.payload,
                created_at=trace.created_at,
            )
            s.add(row)
            s.commit()
        return trace

    def list_session_traces(self, session_id: str, *, limit: int = 50) -> list[SessionTrace]:
        with self._session() as s:
            stmt = (
                select(SessionTraceRow)
                .where(SessionTraceRow.session_id == session_id)
                .order_by(SessionTraceRow.created_at.desc())
                .limit(limit)
            )
            rows = list(s.scalars(stmt).all())
            rows.reverse()
            return [_to_session_trace(r) for r in rows]

    def list_recent_session_traces(self, *, limit: int = 50) -> list[SessionTrace]:
        with self._session() as s:
            stmt = select(SessionTraceRow).order_by(SessionTraceRow.created_at.desc()).limit(limit)
            rows = list(s.scalars(stmt).all())
            return [_to_session_trace(r) for r in rows]

    def list_chat_sessions(self, *, limit: int = 30) -> list[ChatSession]:
        with self._session() as s:
            stmt = select(ChatSessionRow).order_by(ChatSessionRow.updated_at.desc()).limit(limit)
            rows = list(s.scalars(stmt).all())
            return [_to_chat_session(r) for r in rows]

    def reset_chat_session(self, session_id: str) -> bool:
        now = datetime.now(timezone.utc)
        with self._session() as s:
            row = s.get(ChatSessionRow, session_id)
            if row is None:
                return False
            row.messages = []
            row.updated_at = now
            s.commit()
            return True

    def clear_session_traces(self, session_id: str) -> int:
        with self._session() as s:
            stmt = delete(SessionTraceRow).where(SessionTraceRow.session_id == session_id)
            result = s.execute(stmt)
            s.commit()
            return int(result.rowcount or 0)

    # --- Portal de auditoría ---
    def get_audit_portal_progress(self, email: str) -> AuditPortalProgress | None:
        with self._session() as s:
            row = s.get(AuditPortalProgressRow, email)
            if row is None:
                return None
            return AuditPortalProgress(
                email=row.email,
                payload=row.payload or {},
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def save_audit_portal_progress(self, email: str, payload: dict) -> AuditPortalProgress:
        now = datetime.now(timezone.utc)
        with self._session() as s:
            row = s.get(AuditPortalProgressRow, email)
            if row is None:
                row = AuditPortalProgressRow(
                    email=email,
                    payload=payload,
                    created_at=now,
                    updated_at=now,
                )
                s.add(row)
            else:
                row.payload = payload
                row.updated_at = now
            s.commit()
            s.refresh(row)
            return AuditPortalProgress(
                email=row.email,
                payload=row.payload or {},
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def delete_audit_portal_progress(self, email: str) -> bool:
        with self._session() as s:
            row = s.get(AuditPortalProgressRow, email)
            if row is None:
                return False
            s.delete(row)
            s.commit()
            return True

    def get_audit_portal_user(self, email: str) -> AuditPortalUser | None:
        with self._session() as s:
            row = s.get(AuditPortalUserRow, email)
            if row is None:
                return None
            return AuditPortalUser(
                email=row.email,
                pin_hash=row.pin_hash,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def save_audit_portal_user(self, user: AuditPortalUser) -> AuditPortalUser:
        now = datetime.now(timezone.utc)
        with self._session() as s:
            row = s.get(AuditPortalUserRow, user.email)
            if row is None:
                row = AuditPortalUserRow(
                    email=user.email,
                    pin_hash=user.pin_hash,
                    created_at=user.created_at or now,
                    updated_at=now,
                )
                s.add(row)
            else:
                row.pin_hash = user.pin_hash
                row.updated_at = now
            s.commit()
            s.refresh(row)
            return AuditPortalUser(
                email=row.email,
                pin_hash=row.pin_hash,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def record_compliance_consent(self, consent: ComplianceConsent) -> ComplianceConsent:
        with self._session() as s:
            row = ComplianceConsentRow(
                subject_key=consent.subject_key,
                context=consent.context,
                policy_version=consent.policy_version,
                privacy_accepted=consent.privacy_accepted,
                sensitive_data_ack=consent.sensitive_data_ack,
                ip_address=consent.ip_address,
                user_agent=consent.user_agent,
                created_at=consent.created_at,
            )
            s.add(row)
            s.commit()
            s.refresh(row)
            return ComplianceConsent(
                id=row.id,
                subject_key=row.subject_key,
                context=row.context,
                policy_version=row.policy_version,
                privacy_accepted=row.privacy_accepted,
                sensitive_data_ack=row.sensitive_data_ack,
                ip_address=row.ip_address,
                user_agent=row.user_agent,
                created_at=row.created_at,
            )

    def has_valid_compliance_consent(
        self, subject_key: str, *, context: str, policy_version: str
    ) -> bool:
        with self._session() as s:
            stmt = (
                select(ComplianceConsentRow)
                .where(
                    ComplianceConsentRow.subject_key == subject_key,
                    ComplianceConsentRow.context == context,
                    ComplianceConsentRow.policy_version == policy_version,
                    ComplianceConsentRow.privacy_accepted.is_(True),
                    ComplianceConsentRow.sensitive_data_ack.is_(True),
                )
                .order_by(ComplianceConsentRow.created_at.desc())
                .limit(1)
            )
            return s.scalars(stmt).first() is not None

    def log_audit_portal_access(self, entry: AuditPortalAccessLog) -> AuditPortalAccessLog:
        with self._session() as s:
            row = AuditPortalAccessLogRow(
                email=entry.email,
                action=entry.action,
                ip_address=entry.ip_address,
                user_agent=entry.user_agent,
                detail=entry.detail,
                created_at=entry.created_at,
            )
            s.add(row)
            s.commit()
            s.refresh(row)
            return AuditPortalAccessLog(
                id=row.id,
                email=row.email,
                action=row.action,
                ip_address=row.ip_address,
                user_agent=row.user_agent,
                detail=row.detail,
                created_at=row.created_at,
            )

    def append_audit_progress_history(self, email: str, payload: dict, *, keep_last: int = 60) -> None:
        from src.gateway.audit_progress import audit_progress_decision_count

        now = datetime.now(timezone.utc)
        incoming_count = audit_progress_decision_count(payload)
        with self._session() as s:
            last = s.execute(
                select(AuditPortalProgressHistoryRow)
                .where(AuditPortalProgressHistoryRow.email == email)
                .order_by(AuditPortalProgressHistoryRow.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()
            if last is not None:
                last_count = audit_progress_decision_count(last.payload)
                age = (now - last.created_at).total_seconds()
                if incoming_count == last_count and age < 15:
                    return

            s.add(
                AuditPortalProgressHistoryRow(
                    email=email,
                    payload=payload,
                    created_at=now,
                )
            )
            s.flush()

            rows = s.execute(
                select(AuditPortalProgressHistoryRow)
                .where(AuditPortalProgressHistoryRow.email == email)
                .order_by(AuditPortalProgressHistoryRow.created_at.desc())
            ).scalars().all()
            if len(rows) <= keep_last:
                s.commit()
                return

            # Nunca borrar instantáneas con decisiones reales (anti-pérdida).
            protected_ids = {
                row.id
                for row in rows
                if audit_progress_decision_count(row.payload) > 0
            }
            empty_rows = [row for row in rows if row.id not in protected_ids]
            # Mantener las N vacías más recientes; el resto (solo vacías) se puede podar.
            stale_ids = [row.id for row in empty_rows[keep_last:]]

            if stale_ids:
                s.execute(
                    delete(AuditPortalProgressHistoryRow).where(
                        AuditPortalProgressHistoryRow.id.in_(stale_ids)
                    )
                )
            s.commit()

    def get_execution_plan(self, plan_id: str) -> ExecutionPlanRecord | None:
        with self._session() as s:
            row = s.get(ExecutionPlanRow, plan_id)
            return _to_execution_plan(row) if row else None

    def save_execution_plan(self, record: ExecutionPlanRecord) -> ExecutionPlanRecord:
        now = datetime.now(timezone.utc)
        with self._session() as s:
            row = s.get(ExecutionPlanRow, record.plan_id)
            if row is None:
                row = ExecutionPlanRow(plan_id=record.plan_id)
                s.add(row)
            row.session_id = record.session_id
            row.initiator_user_id = record.initiator_user_id
            row.channel = record.channel
            row.user_message = record.user_message
            row.status = record.status
            row.payload = record.payload
            row.updated_at = now
            if row.created_at is None:
                row.created_at = record.created_at or now
            s.commit()
            s.refresh(row)
            return _to_execution_plan(row)

    def list_execution_plans(self, *, limit: int = 50) -> list[ExecutionPlanRecord]:
        from sqlalchemy import select

        with self._session() as s:
            rows = s.scalars(
                select(ExecutionPlanRow).order_by(ExecutionPlanRow.updated_at.desc()).limit(limit)
            ).all()
            return [_to_execution_plan(row) for row in rows]

    def execution_plan_stats(self) -> dict:
        from sqlalchemy import select

        from src.storage.models import aggregate_execution_plan_stats

        with self._session() as s:
            rows = s.scalars(select(ExecutionPlanRow)).all()
            records = [_to_execution_plan(row) for row in rows]
            return aggregate_execution_plan_stats(records)

    def clear_all_execution_plans(self) -> int:
        from sqlalchemy import delete, func, select

        with self._session() as s:
            count = s.scalar(select(func.count()).select_from(ExecutionPlanRow)) or 0
            s.execute(delete(ExecutionPlanRow))
            s.commit()
            return int(count)
