"""Create admin_audit_logs table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-01 00:00:00.000000 UTC
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.String(100), nullable=True),
        # JSONB for efficient querying; stores non-PII action metadata.
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Index for querying by actor (e.g. "show all actions by admin@example.com")
    op.create_index("ix_audit_logs_actor", "admin_audit_logs", ["actor"])
    # Index for querying by action type (e.g. "show all login_failures")
    op.create_index("ix_audit_logs_action", "admin_audit_logs", ["action"])
    # Index for time-based queries — most common access pattern
    op.create_index(
        "ix_audit_logs_created_at",
        "admin_audit_logs",
        ["created_at"],
    )
    # Composite index for resource lookups (e.g. "all actions on contact #X")
    op.create_index(
        "ix_audit_logs_resource",
        "admin_audit_logs",
        ["resource_type", "resource_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_resource", table_name="admin_audit_logs")
    op.drop_index("ix_audit_logs_created_at", table_name="admin_audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="admin_audit_logs")
    op.drop_index("ix_audit_logs_actor", table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")
