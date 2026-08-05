"""
Public-facing Pydantic schema for the availability API.

AvailabilityPublic — the shape returned by GET /api/v1/availability.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class AvailabilityPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    available_from: date | None
    message: str | None
    notice_period_weeks: int | None
