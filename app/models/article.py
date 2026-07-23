"""
Article ORM model.

Stores engineering articles for the public /writing section.

Status lifecycle:
  draft     — being written; invisible to public
  published — live at /writing/{slug}
  archived  — hidden from both public and default admin list

Column notes:
  • slug            — URL-safe identifier; unique; locked once published
  • summary         — 2–3 sentences shown on list cards (no body)
  • body            — full Markdown content
  • tags            — StringArray: ARRAY(String) on PostgreSQL, JSON on SQLite
  • reading_time_minutes — auto-calculated from word count (service layer)
  • featured        — single article promoted on the writing page hero
  • published_at    — set on first publish; not reset on re-publish
  • created_at / updated_at — managed by server_default + onupdate
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, TypeDecorator

from app.db.base import Base


class StringArray(TypeDecorator[list[str]]):
    """
    A list-of-strings column.

    Uses PostgreSQL ARRAY(String) natively in production and JSON in SQLite
    (test environment). This allows the same model to work without changes
    on both databases.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        return dialect.type_descriptor(JSON)

    def process_bind_param(self, value: list[str] | None, dialect: Any) -> Any:  # type: ignore[override]
        if value is None:
            return []
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value: Any, dialect: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return []
        return list(value)


class ArticleStatus(StrEnum):
    DRAFT     = "draft"
    PUBLISHED = "published"
    ARCHIVED  = "archived"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
        unique=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    # body is nullable so drafts can be created without content
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ArticleStatus.DRAFT,
        server_default=ArticleStatus.DRAFT,
    )
    tags: Mapped[list[str]] = mapped_column(
        StringArray(),
        nullable=False,
        default=list,
        server_default="[]",
    )
    reading_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
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
        return f"<Article id={self.id} slug={self.slug!r} status={self.status!r}>"
