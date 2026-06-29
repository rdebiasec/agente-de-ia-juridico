"""chat_sessions y session_traces para conversación multi-turno y trazabilidad

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-29
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("session_id", sa.String(length=120), primary_key=True),
        sa.Column("channel", sa.String(length=20), nullable=False, server_default="web"),
        sa.Column("user_id", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("messages", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    op.create_table(
        "session_traces",
        sa.Column("id", sa.String(length=12), primary_key=True),
        sa.Column("session_id", sa.String(length=120), nullable=False),
        sa.Column("trace_id", sa.String(length=40), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_session_traces_session_id", "session_traces", ["session_id"])
    op.create_index("ix_session_traces_trace_id", "session_traces", ["trace_id"])


def downgrade() -> None:
    op.drop_table("session_traces")
    op.drop_table("chat_sessions")
