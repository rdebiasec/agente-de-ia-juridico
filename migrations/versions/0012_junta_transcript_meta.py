"""Junta del caso — kind/ronda on internal_transcript

Revision ID: 0012
Revises: 0011
Create Date: 2026-08-03

Adds optional deliberation metadata so the lawyer-facing Junta UI can show
ronda and kind (Consulta / Hallazgos / Síntesis) without a second store.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "internal_transcript",
        sa.Column("kind", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "internal_transcript",
        sa.Column("ronda", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("internal_transcript", "ronda")
    op.drop_column("internal_transcript", "kind")
