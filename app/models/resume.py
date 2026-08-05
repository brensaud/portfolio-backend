"""
Resume ORM models.

Five tables covering all resume sections:

  ResumeProfile       — singleton row: headline + summary paragraphs + PDF URL
  ResumeExperience    — experience/employment entries (ordered by sort_order)
  ResumeSkillGroup    — named groups of skills (Backend, AI Engineering, etc.)
  ResumeEducation     — education entries
  ResumeCertification — certifications and learning items
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.types import StringArray


class ResumeProfile(Base):
    """Singleton row — always exactly one row (id = 1)."""

    __tablename__ = "resume_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    headline: Mapped[str] = mapped_column(String(300), nullable=False)
    # Ordered list of summary paragraphs
    summary_paragraphs: Mapped[list[str]] = mapped_column(
        StringArray(),
        nullable=False,
        default=list,
        server_default="[]",
    )
    pdf_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ResumeExperience(Base):
    __tablename__ = "resume_experience"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    role: Mapped[str] = mapped_column(String(200), nullable=False)
    context: Mapped[str] = mapped_column(String(200), nullable=False)
    # period is a free-form string ("2024 – present") — flexible enough for all cases
    period: Mapped[str] = mapped_column(String(100), nullable=False)
    highlights: Mapped[list[str]] = mapped_column(
        StringArray(),
        nullable=False,
        default=list,
        server_default="[]",
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ResumeSkillGroup(Base):
    __tablename__ = "resume_skill_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    group_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skills: Mapped[list[str]] = mapped_column(
        StringArray(),
        nullable=False,
        default=list,
        server_default="[]",
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ResumeEducation(Base):
    __tablename__ = "resume_education"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str] = mapped_column(String(200), nullable=False)
    # status: Completed / In progress / Planned / Self-directed
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ResumeCertification(Base):
    __tablename__ = "resume_certifications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(200), nullable=False)
    # status: Completed / In progress / Planned / Self-directed
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
