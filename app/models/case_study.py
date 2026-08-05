"""
CaseStudy ORM model.

Each row represents one project's deep-dive case study.  The rich nested
content (architecture, decisions, roadmap, etc.) is stored in a single JSON
column — this avoids the complexity of 15+ join tables for a portfolio CMS
while keeping every field queryable at the application level.

Column notes:
  slug       — matches the project slug; unique; used as the public lookup key
  status     — 'draft' (default, hidden from public) | 'published'
  disclaimer — optional note shown in the case study hero
  content    — full nested case study body (see CaseStudy interface in
               frontend/src/data/case-studies.ts for the canonical shape)
  published_at — set on first publish; not reset on re-publish
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class CaseStudyStatus(StrEnum):
    DRAFT     = "draft"
    PUBLISHED = "published"


class CaseStudy(Base):
    __tablename__ = "case_studies"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Matches the project slug — used as the public lookup key.
    slug: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
        unique=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=CaseStudyStatus.DRAFT,
        server_default=CaseStudyStatus.DRAFT,
    )
    disclaimer: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Full nested case study body; shape matches the CaseStudy TS interface.
    content: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<CaseStudy slug={self.slug!r} status={self.status!r}>"
