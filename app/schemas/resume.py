"""
Public Pydantic schemas for the resume endpoint.

ResumePublic — complete resume response for GET /api/v1/resume.
All nested models are read-only (no input validation needed here).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeProfilePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    headline: str
    summary_paragraphs: list[str]
    pdf_url: str | None
    updated_at: datetime


class ResumeExperiencePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    context: str
    period: str
    highlights: list[str]
    sort_order: int


class ResumeSkillGroupPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    group_name: str
    skills: list[str]
    sort_order: int


class ResumeEducationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution: str
    degree: str
    status: str
    notes: str | None
    sort_order: int


class ResumeCertificationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    provider: str
    status: str
    sort_order: int


class ResumePublic(BaseModel):
    """Complete resume — returned by GET /api/v1/resume."""

    profile: ResumeProfilePublic
    experience: list[ResumeExperiencePublic]
    skill_groups: list[ResumeSkillGroupPublic]
    education: list[ResumeEducationPublic]
    certifications: list[ResumeCertificationPublic]
