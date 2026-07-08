"""execution_plans — planes de ejecución aprobados por el abogado

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-06
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "execution_plans",
        sa.Column("plan_id", sa.Text(), primary_key=True),
        sa.Column("session_id", sa.Text(), nullable=False, index=True),
        sa.Column("initiator_user_id", sa.Text(), nullable=False),
        sa.Column("channel", sa.Text(), nullable=False, server_default="web"),
        sa.Column("user_message", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("execution_plans")
