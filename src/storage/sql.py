"""Backend SQLAlchemy/Postgres + pgvector (paridad dev==prod vía Docker o Render).

Se activa cuando `DATABASE_URL` está configurado. Incluye la tabla de
fragmentos con embeddings para RAG (búsqueda por similitud coseno).
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Date, DateTime, Float, String, Text, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from src.storage.models import Deadline, DocumentChunk, Draft, EMBED_DIM, Expediente


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


def _to_draft(row: DraftRow) -> Draft:
    return Draft(
        id=row.id,
        session_id=row.session_id,
        tipo=row.tipo,
        titulo=row.titulo,
        contenido=row.contenido,
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
        actualizado_en=row.actualizado_en or 0.0,
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
        with self._session() as s:
            row = DraftRow(
                id=draft.id,
                session_id=draft.session_id,
                tipo=draft.tipo,
                titulo=draft.titulo,
                contenido=draft.contenido,
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
        with self._session() as s:
            row = s.get(DraftRow, draft_id)
            if row is None:
                return None
            for key, value in changes.items():
                if hasattr(row, key):
                    setattr(row, key, value)
            row.updated_at = datetime.now(timezone.utc)
            s.commit()
            return _to_draft(row)

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
            row.actualizado_en = expediente.actualizado_en
            s.commit()
        return expediente
