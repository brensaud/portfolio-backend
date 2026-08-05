"""Create page_views table

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-05 00:00:00.000000 UTC

One table:
  page_views — privacy-first analytics; IP is never stored.

Design notes:
  - No seed data — analytics begins accumulating from first deploy
  - Indexed on created_at (time-range queries), path (top-pages), and
    the (session_id, path, created_at) composite for deduplication checks
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "page_views",
        sa.Column("id",         sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("path",       sa.String(500), nullable=False),
        sa.Column("referrer",   sa.String(500), nullable=True),
        sa.Column("country",    sa.String(2),   nullable=True),
        sa.Column("session_id", sa.String(64),  nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_page_views_created_at",   "page_views", ["created_at"])
    op.create_index("ix_page_views_path",          "page_views", ["path"])
    op.create_index("ix_page_views_session_path",  "page_views", ["session_id", "path", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_page_views_session_path", table_name="page_views")
    op.drop_index("ix_page_views_path",          table_name="page_views")
    op.drop_index("ix_page_views_created_at",    table_name="page_views")
    op.drop_table("page_views")
