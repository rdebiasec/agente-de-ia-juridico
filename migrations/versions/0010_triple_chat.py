"""Triple chat — client threads, internal transcript, outbound drafts

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-02
"""

from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "expedientes",
        sa.Column("lawyer_session_id", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "expedientes",
        sa.Column("cliente_session_id", sa.String(length=120), nullable=True),
    )
    op.create_index(
        "ix_expedientes_cliente_session_id",
        "expedientes",
        ["cliente_session_id"],
    )

    op.create_table(
        "client_threads",
        sa.Column("thread_id", sa.String(length=12), primary_key=True),
        sa.Column("cliente_session_id", sa.String(length=120), nullable=False),
        sa.Column("lawyer_session_id", sa.String(length=120), nullable=False),
        sa.Column("expediente_session_id", sa.String(length=120), nullable=False),
        sa.Column("subject_label", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_client_threads_cliente_session_id",
        "client_threads",
        ["cliente_session_id"],
        unique=True,
    )
    op.create_index(
        "ix_client_threads_lawyer_session_id",
        "client_threads",
        ["lawyer_session_id"],
    )

    op.create_table(
        "client_messages",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("thread_id", sa.String(length=12), nullable=False, index=True),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("visibility", sa.String(length=20), nullable=False),
        sa.Column("outbound_draft_id", sa.String(length=12), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "internal_transcript",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("session_id", sa.String(length=120), nullable=False, index=True),
        sa.Column("from_actor", sa.String(length=80), nullable=False),
        sa.Column("to_actor", sa.String(length=80), nullable=False),
        sa.Column("pedido", sa.Text(), nullable=False, server_default=""),
        sa.Column("respuesta", sa.Text(), nullable=False, server_default=""),
        sa.Column("turn_ref", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "outbound_client_drafts",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("thread_id", sa.String(length=12), nullable=False, index=True),
        sa.Column("lawyer_session_id", sa.String(length=120), nullable=False, index=True),
        sa.Column("cliente_session_id", sa.String(length=120), nullable=False, index=True),
        sa.Column("inbound_message_id", sa.String(length=12), nullable=True),
        sa.Column("proposed_text", sa.Text(), nullable=False),
        sa.Column("final_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, index=True),
        sa.Column("revisor", sa.String(length=120), nullable=True),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("outbound_client_drafts")
    op.drop_table("internal_transcript")
    op.drop_table("client_messages")
    op.drop_index("ix_client_threads_lawyer_session_id", table_name="client_threads")
    op.drop_index("ix_client_threads_cliente_session_id", table_name="client_threads")
    op.drop_table("client_threads")
    op.drop_index("ix_expedientes_cliente_session_id", table_name="expedientes")
    op.drop_column("expedientes", "cliente_session_id")
    op.drop_column("expedientes", "lawyer_session_id")
