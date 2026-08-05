"""
Public-facing Pydantic schema for profile settings.

ProfilePublic — the shape returned by GET /api/v1/settings/profile.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ProfilePublic(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    role: str
    tagline: str
    bio: str | None
    github: str | None
    linkedin: str | None
    email: str | None
    twitter_handle: str | None
