"""compliance — consentimiento, PIN, logs y historial del portal de auditoría

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "compliance_consent",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("subject_key", sa.Text(), nullable=False),
        sa.Column("context", sa.Text(), nullable=False),
        sa.Column("policy_version", sa.Text(), nullable=False),
        sa.Column("privacy_accepted", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sensitive_data_ack", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ip_address", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_compliance_consent_subject", "compliance_consent", ["subject_key", "context"])

    op.create_table(
        "audit_portal_user",
        sa.Column("email", sa.Text(), primary_key=True),
        sa.Column("pin_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "audit_portal_access_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("ip_address", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_access_log_email", "audit_portal_access_log", ["email"])
    op.create_index("ix_audit_access_log_created", "audit_portal_access_log", ["created_at"])

    op.create_table(
        "audit_portal_progress_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_progress_hist_email", "audit_portal_progress_history", ["email"])


def downgrade() -> None:
    op.drop_table("audit_portal_progress_history")
    op.drop_table("audit_portal_access_log")
    op.drop_table("audit_portal_user")
    op.drop_table("compliance_consent")
