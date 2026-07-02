"""Update contact_messages status enum values and add composite index

Rename legacy status strings to match the Sprint 2 admin lifecycle:
  "new"     → "unread"   (initial state — not yet viewed by admin)
  "replied" → "read"     (fold into the read state; no data loss)

The "read" value is unchanged.

A composite index on (status, created_at DESC) is added to support the
primary admin list query pattern: filter-by-status + order-by-date.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-02 00:00:00.000000 UTC
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Data migration (idempotent) ───────────────────────────────────────────
    # Run before altering server_default so existing rows are normalised first.
    op.execute("UPDATE contact_messages SET status = 'unread' WHERE status = 'new'")
    op.execute("UPDATE contact_messages SET status = 'read' WHERE status = 'replied'")

    # ── Column server_default ─────────────────────────────────────────────────
    # New submissions must default to 'unread'.
    op.alter_column(
        "contact_messages",
        "status",
        server_default="unread",
        existing_type=sa.String(20),
        existing_nullable=False,
    )

    # ── Composite index for admin list queries ────────────────────────────────
    # Covers: WHERE status = ? ORDER BY created_at DESC
    op.create_index(
        "ix_contact_messages_status_created_at",
        "contact_messages",
        ["status", sa.text("created_at DESC")],
        # postgresql_using is not required for a standard B-tree index.
        # The DESC ordering hint is advisory on some backends.
    )


def downgrade() -> None:
    op.drop_index(
        "ix_contact_messages_status_created_at",
        table_name="contact_messages",
    )

    op.alter_column(
        "contact_messages",
        "status",
        server_default="new",
        existing_type=sa.String(20),
        existing_nullable=False,
    )

    # Reverse data migration (best-effort; "archived" has no prior equivalent)
    op.execute("UPDATE contact_messages SET status = 'new' WHERE status = 'unread'")
    # archived → no clean reverse; leave as-is to avoid data loss on downgrade
