"""Client thread/message meta — consent, display name, authored_by

Revision ID: 0013
Revises: 0012
Create Date: 2026-08-04

JSON meta on client_threads (consent_at, client_display_name, contact)
and client_messages (authored_by=lawyer_impersonation, lawyer_actor_id).
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "client_threads",
        sa.Column("meta", sa.JSON(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "client_messages",
        sa.Column("meta", sa.JSON(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("client_messages", "meta")
    op.drop_column("client_threads", "meta")
