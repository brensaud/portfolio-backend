"""Create site_settings table

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-05 00:00:00.000000 UTC
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SEED_ROWS = [
    {"key": "profile.name",           "value": "Bren Saud"},
    {"key": "profile.role",           "value": "Python Backend Engineer"},
    {"key": "profile.tagline",        "value": "Building production-grade backend systems and AI products."},
    {"key": "profile.bio",            "value": None},
    {"key": "profile.github",         "value": "https://github.com/brensaud"},
    {"key": "profile.linkedin",       "value": None},
    {"key": "profile.email",          "value": None},
    {"key": "profile.twitter_handle", "value": None},
]


def upgrade() -> None:
    t = op.create_table(
        "site_settings",
        sa.Column("key",   sa.String(100), primary_key=True),
        sa.Column("value", sa.Text(),      nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.bulk_insert(t, _SEED_ROWS)


def downgrade() -> None:
    op.drop_table("site_settings")
