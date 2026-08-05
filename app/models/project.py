"""
Project ORM model.

Stores portfolio projects for the public /work section.

Status lifecycle:
  draft     — being built; invisible to public
  published — live at /work/{slug}
  archived  — hidden from both public and default admin list

Column notes:
  • slug          — URL-safe identifier; unique; server-generated from title
  • display_order — integer used to control the listed order; lower = higher priority
  • tech_stack    — StringArray: ARRAY(String) on PostgreSQL, JSON on SQLite
  • links         — JSON list of { label, href, type } objects
  • is_featured   — multi-select flag; multiple projects may be featured
  • thumbnail_url — fully-qualified external URL (CDN-hosted image)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text, Uuid, func
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.types import StringArray


class ProjectStatus(StrEnum):
    DRAFT     = "draft"
    PUBLISHED = "published"
    ARCHIVED  = "archived"


class Project(Base):
    __tablename__ = "projects"

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
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ProjectStatus.DRAFT,
        server_default=ProjectStatus.DRAFT,
    )
    tech_stack: Mapped[list[str]] = mapped_column(
        StringArray(),
        nullable=False,
        default=list,
        server_default="[]",
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    links: Mapped[list[Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default="[]",
    )
    thumbnail_url: Mapped[str | None] = mapped_column(
        String(500),
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
