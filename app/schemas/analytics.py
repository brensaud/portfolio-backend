"""Public analytics schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PageViewCreate(BaseModel):
    """Body for POST /api/v1/analytics/view."""

    path: str = Field(min_length=1, max_length=500)
    referrer: str | None = Field(default=None, max_length=500)
    # Anonymous random UUID from browser sessionStorage
    session_id: str = Field(min_length=1, max_length=64)

    model_config = {"extra": "forbid"}
