"""
Admin-facing Pydantic schemas for site settings.

AdminProfileOut — response body for GET and PUT /admin/api/settings/profile.
ProfileUpdate   — request body for PUT /admin/api/settings/profile.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AdminProfileOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    role: str
    tagline: str
    bio: str | None
    github: str | None
    linkedin: str | None
    email: str | None
    twitter_handle: str | None


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    tagline: str = Field(min_length=1, max_length=500)
    bio: str | None = Field(default=None, max_length=2000)
    github: str | None = Field(default=None, max_length=300)
    linkedin: str | None = Field(default=None, max_length=300)
    email: str | None = Field(default=None, max_length=300)
    twitter_handle: str | None = Field(default=None, max_length=100)
