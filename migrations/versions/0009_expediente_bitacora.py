"""expedientes — bitácora de notas Gerente + especialistas

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "expedientes",
        sa.Column("bitacora", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("expedientes", "bitacora")
