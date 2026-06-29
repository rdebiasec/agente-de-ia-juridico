"""esquema inicial de la firma (drafts, expedientes, deadlines, document_chunks)

Revision ID: 0001
Revises:
Create Date: 2026-06-28
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from src.storage.models import EMBED_DIM

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "drafts",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("session_id", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("tipo", sa.String(length=40), nullable=False, server_default="documento"),
        sa.Column("titulo", sa.String(length=300), nullable=False, server_default=""),
        sa.Column("contenido", sa.Text(), nullable=False, server_default=""),
        sa.Column("materia", sa.String(length=40), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default="propuesto"),
        sa.Column("revisor", sa.String(length=120), nullable=True),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("slack_ts", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_drafts_session_id", "drafts", ["session_id"])
    op.create_index("ix_drafts_estado", "drafts", ["estado"])

    op.create_table(
        "expedientes",
        sa.Column("session_id", sa.String(length=120), primary_key=True),
        sa.Column("materia", sa.String(length=40), nullable=True),
        sa.Column("tipo_proceso", sa.String(length=60), nullable=True),
        sa.Column("rol_despacho", sa.String(length=40), nullable=True),
        sa.Column("radicado", sa.String(length=120), nullable=True),
        sa.Column("despacho_judicial", sa.String(length=200), nullable=True),
        sa.Column("etapa_actual", sa.String(length=120), nullable=True),
        sa.Column("partes", sa.JSON(), nullable=True),
        sa.Column("terminos", sa.JSON(), nullable=True),
        sa.Column("actualizado_en", sa.Float(), nullable=False, server_default="0"),
    )

    op.create_table(
        "deadlines",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("session_id", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("descripcion", sa.Text(), nullable=False, server_default=""),
        sa.Column("tipo", sa.String(length=40), nullable=False, server_default="termino"),
        sa.Column("fecha_base", sa.Date(), nullable=True),
        sa.Column("fecha_limite", sa.Date(), nullable=True),
        sa.Column("dias_habiles", sa.Integer(), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default="pendiente"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_deadlines_session_id", "deadlines", ["session_id"])
    op.create_index("ix_deadlines_fecha_limite", "deadlines", ["fecha_limite"])
    op.create_index("ix_deadlines_estado", "deadlines", ["estado"])

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("scope", sa.String(length=20), nullable=False, server_default="kb"),
        sa.Column("expediente_id", sa.String(length=120), nullable=True),
        sa.Column("fuente", sa.Text(), nullable=False, server_default=""),
        sa.Column("chunk_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding", Vector(EMBED_DIM), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_document_chunks_scope", "document_chunks", ["scope"])
    op.create_index("ix_document_chunks_expediente_id", "document_chunks", ["expediente_id"])


def downgrade() -> None:
    op.drop_table("document_chunks")
    op.drop_table("deadlines")
    op.drop_table("expedientes")
    op.drop_table("drafts")
