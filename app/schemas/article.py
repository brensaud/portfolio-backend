"""
Public-facing Pydantic schemas for the articles API.

ArticleListItem   — compact shape for list responses (no body).
ArticlePublic     — full shape for the detail endpoint (includes body).
ArticlesPage      — pagination envelope for GET /api/v1/articles.

Design notes:
  • body is excluded from ArticleListItem to keep list payloads small.
  • All schemas use from_attributes=True for direct ORM serialisation.
  • tags is a list[str] — serialised from PostgreSQL TEXT[].
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArticleListItem(BaseModel):
    """Compact article shape returned in list responses. Body excluded."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    summary: str
    category: str
    tags: list[str]
    reading_time_minutes: int | None
    featured: bool
    published_at: datetime
    updated_at: datetime


class ArticlePublic(BaseModel):
    """Full article shape returned by the detail endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    summary: str
    body: str | None
    category: str
    tags: list[str]
    reading_time_minutes: int | None
    featured: bool
    published_at: datetime
    updated_at: datetime


class ArticlesPage(BaseModel):
    """Pagination envelope for GET /api/v1/articles."""

    items: list[ArticleListItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)
