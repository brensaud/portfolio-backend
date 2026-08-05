"""
Admin-facing Pydantic schemas for availability management.

AdminAvailabilityOut — shape returned by GET and PUT /admin/api/availability.
AvailabilityUpdate   — request body for PUT /admin/api/availability.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AdminAvailabilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    status: str
    available_from: date | None
    message: str | None
    notice_period_weeks: int | None
    updated_at: datetime


class AvailabilityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["available", "limited", "unavailable"]
    available_from: date | None = Field(default=None)
    message: str | None = Field(default=None, max_length=500)
    notice_period_weeks: int | None = Field(default=None, ge=1, le=52)
