"""
Admin-facing Pydantic schemas for project management.

AdminProjectSummary  — compact shape for the admin list.
AdminProjectDetail   — full shape for editor and mutation responses.
ProjectCreate        — POST /admin/api/projects body.
ProjectUpdate        — PUT /admin/api/projects/{id} body (all fields optional).
ProjectReorderItem   — single item in a reorder request.
ProjectReorderRequest — PATCH /admin/api/projects/reorder body.
AdminProjectsPage    — pagination envelope.

Design:
  • extra="forbid" on all input schemas.
  • from_attributes=True on output schemas.
  • thumbnail_url validated as http/https on input.
  • links.href validated as http/https on input.
  • slug is server-generated; never in input schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Shared link shape ─────────────────────────────────────────────────────────


class ProjectLinkInput(BaseModel):
    """Validated link for create/update requests."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=100)
    href: str = Field(min_length=1, max_length=500)
    type: Literal["github", "demo", "case-study", "article"]

    @field_validator("href")
    @classmethod
    def href_must_be_http(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("Link href must be an http or https URL.")
        return v


# ── Output schemas ────────────────────────────────────────────────────────────


class AdminProjectSummary(BaseModel):
    """Compact shape for the admin project list."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    slug: str
    title: str
    subtitle: str | None
    category: str
    status: str
    is_featured: bool
    display_order: int
    thumbnail_url: str | None
    created_at: datetime
    updated_at: datetime


class AdminProjectDetail(BaseModel):
    """Full shape for the project editor and all mutation responses."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    slug: str
    title: str
    subtitle: str | None
    description: str
    category: str
    status: str
    tech_stack: list[str]
    is_featured: bool
    display_order: int
    links: list[Any]
    thumbnail_url: str | None
    created_at: datetime
    updated_at: datetime


class AdminProjectsPage(BaseModel):
    items: list[AdminProjectSummary]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)


# ── Input schemas ─────────────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    """Request body for POST /admin/api/projects."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=300)
    subtitle: str | None = Field(default=None, max_length=500)
    description: str = Field(min_length=1, max_length=5000)
    category: str = Field(min_length=1, max_length=50)
    tech_stack: list[str] = Field(default_factory=list, max_length=20)
    is_featured: bool = Field(default=False)
    display_order: int = Field(default=0, ge=0, le=9999)
    links: list[ProjectLinkInput] = Field(default_factory=list, max_length=10)
    thumbnail_url: str | None = Field(default=None)

    @field_validator("tech_stack")
    @classmethod
    def tech_stack_item_length(cls, v: list[str]) -> list[str]:
        for item in v:
            if len(item) > 50:
                raise ValueError("Each tech_stack item must be at most 50 characters.")
        return v

    @field_validator("thumbnail_url", mode="before")
    @classmethod
    def thumbnail_must_be_http(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str) or not v.startswith(("http://", "https://")):
            raise ValueError("thumbnail_url must be an http or https URL.")
        return v


class ProjectUpdate(BaseModel):
    """Request body for PUT /admin/api/projects/{id}. All fields optional."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=300)
    subtitle: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    tech_stack: list[str] | None = Field(default=None, max_length=20)
    is_featured: bool | None = Field(default=None)
    display_order: int | None = Field(default=None, ge=0, le=9999)
    links: list[ProjectLinkInput] | None = Field(default=None, max_length=10)
    thumbnail_url: str | None = Field(default=None)
    # Explicit sentinel: set to True to clear thumbnail_url to null
    clear_thumbnail: bool = Field(default=False)

    @field_validator("tech_stack")
    @classmethod
    def tech_stack_item_length(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        for item in v:
            if len(item) > 50:
                raise ValueError("Each tech_stack item must be at most 50 characters.")
        return v

    @field_validator("thumbnail_url", mode="before")
    @classmethod
    def thumbnail_must_be_http(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str) or not v.startswith(("http://", "https://")):
            raise ValueError("thumbnail_url must be an http or https URL.")
        return v


class ProjectReorderItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    display_order: int = Field(ge=0, le=9999)


class ProjectReorderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ProjectReorderItem] = Field(min_length=1, max_length=200)
