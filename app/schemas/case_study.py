"""Public schemas for the case study API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CaseStudyPublic(BaseModel):
    slug: str
    disclaimer: str | None
    status: str
    published_at: datetime | None
    content: dict

    model_config = {"from_attributes": True}
