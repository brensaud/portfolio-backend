"""Create articles table

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-23 00:00:00.000000 UTC
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(250), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("reading_time_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "featured",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_articles_slug"),
    )

    # Unique index on slug (primary lookup path for public detail endpoint)
    op.create_index("ix_articles_slug", "articles", ["slug"], unique=True)

    # Filter by status (admin list, public list always uses status='published')
    op.create_index("ix_articles_status", "articles", ["status"])

    # Order public list by published_at DESC
    op.create_index(
        "ix_articles_published_at",
        "articles",
        [sa.text("published_at DESC")],
    )

    # Composite: filter-by-status + order-by-date (covers both public and admin)
    op.create_index(
        "ix_articles_status_published_at",
        "articles",
        ["status", sa.text("published_at DESC")],
    )

    # Quick lookup of the featured article (WHERE featured = true)
    op.create_index(
        "ix_articles_featured",
        "articles",
        ["featured"],
        postgresql_where=sa.text("featured = true"),
    )


def downgrade() -> None:
    op.drop_index("ix_articles_featured", table_name="articles")
    op.drop_index("ix_articles_status_published_at", table_name="articles")
    op.drop_index("ix_articles_published_at", table_name="articles")
    op.drop_index("ix_articles_status", table_name="articles")
    op.drop_index("ix_articles_slug", table_name="articles")
    op.drop_table("articles")
