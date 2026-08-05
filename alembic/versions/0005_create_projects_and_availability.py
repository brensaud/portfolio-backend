"""Create projects and availability tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-05 00:00:00.000000 UTC
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── projects ──────────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(250), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("subtitle", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "tech_stack",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "is_featured",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "links",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
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
    )
    op.create_index("ix_projects_slug", "projects", ["slug"], unique=True)
    # Covers: WHERE status = ? ORDER BY display_order ASC
    op.create_index(
        "ix_projects_status_display_order",
        "projects",
        ["status", "display_order"],
    )
    # Covers: WHERE status = 'published' AND is_featured = true
    op.create_index(
        "ix_projects_status_is_featured",
        "projects",
        ["status", "is_featured"],
    )

    # ── availability ──────────────────────────────────────────────────────────
    op.create_table(
        "availability",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="available",
        ),
        sa.Column("available_from", sa.Date(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("notice_period_weeks", sa.Integer(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Seed the single availability row
    op.execute(
        "INSERT INTO availability (id, status) VALUES (1, 'available')"
    )


def downgrade() -> None:
    op.drop_table("availability")
    op.drop_index("ix_projects_status_is_featured", table_name="projects")
    op.drop_index("ix_projects_status_display_order", table_name="projects")
    op.drop_index("ix_projects_slug", table_name="projects")
    op.drop_table("projects")
