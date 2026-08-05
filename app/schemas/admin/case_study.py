"""Admin schemas for the case study CMS."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AdminCaseStudyOut(BaseModel):
    id: uuid.UUID
    slug: str
    status: str
    disclaimer: str | None
    content: dict
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminCaseStudyCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=250)
    disclaimer: str | None = None
    content: dict = Field(default_factory=dict)

    model_config = {"extra": "forbid"}


class AdminCaseStudyUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=250)
    disclaimer: str | None = None
    content: dict | None = None

    model_config = {"extra": "forbid"}
