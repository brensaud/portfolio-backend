"""
Admin-facing Pydantic schemas for article management.

AdminArticleSummary — compact shape for the admin list (no body).
AdminArticleDetail  — full shape for the editor and mutation responses.
ArticleCreate       — request body for POST /admin/api/articles.
ArticleUpdate       — request body for PUT /admin/api/articles/{id}.
AdminArticlesPage   — pagination envelope for GET /admin/api/articles.

Design notes:
  • extra="forbid" on all schemas prevents parameter pollution.
  • body is excluded from AdminArticleSummary — admin list does not need it.
  • ArticleUpdate uses all-optional fields so partial updates are natural.
  • slug is not in ArticleCreate — generated from title server-side.
  • slug is not in ArticleUpdate — locked once published (service enforces).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminArticleSummary(BaseModel):
    """Compact shape for admin list. Body excluded."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    slug: str
    title: str
    summary: str
    category: str
    status: str
    tags: list[str]
    reading_time_minutes: int | None
    featured: bool
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminArticleDetail(BaseModel):
    """Full shape for the article editor and all mutation responses."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    slug: str
    title: str
    summary: str
    body: str | None
    category: str
    status: str
    tags: list[str]
    reading_time_minutes: int | None
    featured: bool
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ArticleCreate(BaseModel):
    """Request body for POST /admin/api/articles (create draft)."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(min_length=1, max_length=2000)
    body: str | None = Field(default=None)
    category: str = Field(min_length=1, max_length=50)
    tags: list[str] = Field(default_factory=list, max_length=10)
    featured: bool = Field(default=False)


class ArticleUpdate(BaseModel):
    """Request body for PUT /admin/api/articles/{id}. All fields optional."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=300)
    summary: str | None = Field(default=None, min_length=1, max_length=2000)
    body: str | None = Field(default=None)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    tags: list[str] | None = Field(default=None, max_length=10)
    featured: bool | None = Field(default=None)


class AdminArticlesPage(BaseModel):
    """Pagination envelope for GET /admin/api/articles."""

    model_config = ConfigDict(extra="forbid")

    items: list[AdminArticleSummary]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)
