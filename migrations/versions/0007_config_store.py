"""config_versions + config_active — almacén versionado de prompts/guardrails/skills

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-24
"""

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "config_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("checksum", sa.Text(), nullable=False),
        sa.Column("author_email", sa.Text(), nullable=False, server_default=""),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("kind", "key", "version", name="uq_config_versions_kind_key_ver"),
    )
    op.create_index("ix_config_versions_kind_key", "config_versions", ["kind", "key"])

    op.create_table(
        "config_active",
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("active_version", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.Text(), nullable=False),
        sa.Column("path", sa.Text(), nullable=False, server_default=""),
        sa.Column("updated_by", sa.Text(), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("kind", "key", name="pk_config_active"),
    )


def downgrade() -> None:
    op.drop_table("config_active")
    op.drop_index("ix_config_versions_kind_key", table_name="config_versions")
    op.drop_table("config_versions")
