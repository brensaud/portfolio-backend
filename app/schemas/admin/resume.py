"""
Admin Pydantic schemas for resume management endpoints.

All input schemas use extra="forbid" to reject unknown fields.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ── Credential status literal ─────────────────────────────────────────────────

CredentialStatus = Literal["Completed", "In progress", "Planned", "Self-directed"]

# ── Profile ───────────────────────────────────────────────────────────────────


class AdminResumeProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    headline: str
    summary_paragraphs: list[str]
    pdf_url: str | None
    updated_at: datetime


class ResumeProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headline: str = Field(min_length=1, max_length=300)
    summary_paragraphs: list[str] = Field(default_factory=list)
    pdf_url: str | None = Field(default=None, max_length=500)

# ── Experience ────────────────────────────────────────────────────────────────


class AdminResumeExperienceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    context: str
    period: str
    highlights: list[str]
    sort_order: int
    updated_at: datetime


class ResumeExperienceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str = Field(min_length=1, max_length=200)
    context: str = Field(min_length=1, max_length=200)
    period: str = Field(min_length=1, max_length=100)
    highlights: list[str] = Field(default_factory=list)


class ResumeExperienceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str = Field(min_length=1, max_length=200)
    context: str = Field(min_length=1, max_length=200)
    period: str = Field(min_length=1, max_length=100)
    highlights: list[str] = Field(default_factory=list)

# ── Skill groups ──────────────────────────────────────────────────────────────


class AdminResumeSkillGroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    group_name: str
    skills: list[str]
    sort_order: int
    updated_at: datetime


class ResumeSkillGroupCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_name: str = Field(min_length=1, max_length=100)
    skills: list[str] = Field(default_factory=list)


class ResumeSkillGroupUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_name: str = Field(min_length=1, max_length=100)
    skills: list[str] = Field(default_factory=list)

# ── Education ─────────────────────────────────────────────────────────────────


class AdminResumeEducationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution: str
    degree: str
    status: str
    notes: str | None
    sort_order: int
    updated_at: datetime


class ResumeEducationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: str = Field(min_length=1, max_length=200)
    degree: str = Field(min_length=1, max_length=200)
    status: CredentialStatus
    notes: str | None = None


class ResumeEducationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: str = Field(min_length=1, max_length=200)
    degree: str = Field(min_length=1, max_length=200)
    status: CredentialStatus
    notes: str | None = None

# ── Certifications ────────────────────────────────────────────────────────────


class AdminResumeCertificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    provider: str
    status: str
    sort_order: int
    updated_at: datetime


class ResumeCertificationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    provider: str = Field(min_length=1, max_length=200)
    status: CredentialStatus


class ResumeCertificationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    provider: str = Field(min_length=1, max_length=200)
    status: CredentialStatus

# ── Full admin resume response ────────────────────────────────────────────────


class AdminResumeOut(BaseModel):
    """Complete resume returned by GET /admin/api/resume."""

    profile: AdminResumeProfileOut
    experience: list[AdminResumeExperienceOut]
    skill_groups: list[AdminResumeSkillGroupOut]
    education: list[AdminResumeEducationOut]
    certifications: list[AdminResumeCertificationOut]
