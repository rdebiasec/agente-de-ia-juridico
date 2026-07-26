"""expedientes — ledger y métricas del loop de gerencia

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-25
"""

from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "expedientes",
        sa.Column("hechos_minimos_confirmados", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "expedientes",
        sa.Column("poder_acreditado", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "expedientes",
        sa.Column("ultima_actuacion_confirmada", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "expedientes",
        sa.Column("faltantes_gerencia", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "expedientes",
        sa.Column("tareas_gerencia", sa.JSON(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "expedientes",
        sa.Column("metricas_gerencia", sa.JSON(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("expedientes", "metricas_gerencia")
    op.drop_column("expedientes", "tareas_gerencia")
    op.drop_column("expedientes", "faltantes_gerencia")
    op.drop_column("expedientes", "ultima_actuacion_confirmada")
    op.drop_column("expedientes", "poder_acreditado")
    op.drop_column("expedientes", "hechos_minimos_confirmados")

