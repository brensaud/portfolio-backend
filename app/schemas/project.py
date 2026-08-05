"""
Public-facing Pydantic schemas for the projects API.

ProjectLink      — shape for individual project links.
ProjectListItem  — compact shape for list responses.
ProjectPublic    — full shape for the detail endpoint.
ProjectsPage     — pagination envelope for GET /api/v1/projects.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectLink(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str
    href: str
    type: str


class ProjectListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    links: list[ProjectLink]
    thumbnail_url: str | None
    created_at: datetime
    updated_at: datetime


class ProjectPublic(ProjectListItem):
    """Full project shape — identical to list item for projects (no separate body field)."""


class ProjectsPage(BaseModel):
    items: list[ProjectListItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)
