"""
ResumeRepository — data access for all resume tables.

All write methods call session.flush() but do NOT commit; the service layer
owns the transaction boundary.

Methods:
  get_profile()              — fetch singleton profile row (or create default)
  update_profile()           — update headline / paragraphs / pdf_url

  list_experience()          — all experience rows ordered by sort_order
  create_experience()        — insert new row; assigns sort_order = max + 1
  update_experience()        — update existing row
  delete_experience()        — delete by id

  list_skill_groups()        — all skill group rows ordered by sort_order
  create_skill_group()       — insert new row
  update_skill_group()       — update existing row
  delete_skill_group()       — delete by id

  list_education()           — all education rows ordered by sort_order
  create_education()         — insert new row
  update_education()         — update existing row
  delete_education()         — delete by id

  list_certifications()      — all cert rows ordered by sort_order
  create_certification()     — insert new row
  update_certification()     — update existing row
  delete_certification()     — delete by id
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import (
    ResumeCertification,
    ResumeEducation,
    ResumeExperience,
    ResumeProfile,
    ResumeSkillGroup,
)

logger = logging.getLogger(__name__)

_PROFILE_ID = 1

_DEFAULT_HEADLINE = "Python backend engineer focused on FastAPI, AI SaaS, and production-grade systems."
_DEFAULT_PARAGRAPHS: list[str] = []


class ResumeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._s = session

    # ── Profile ───────────────────────────────────────────────────────────────

    async def get_profile(self) -> ResumeProfile:
        """Return the singleton profile row, creating it with defaults if absent."""
        stmt = select(ResumeProfile).where(ResumeProfile.id == _PROFILE_ID)
        row = (await self._s.execute(stmt)).scalar_one_or_none()
        if row is None:
            row = ResumeProfile(
                id=_PROFILE_ID,
                headline=_DEFAULT_HEADLINE,
                summary_paragraphs=_DEFAULT_PARAGRAPHS,
            )
            self._s.add(row)
            await self._s.flush()
            await self._s.refresh(row)
        return row

    async def update_profile(
        self,
        *,
        headline: str,
        summary_paragraphs: list[str],
        pdf_url: str | None,
    ) -> ResumeProfile:
        """Update the singleton profile row. Does NOT commit."""
        row = await self.get_profile()
        row.headline = headline
        row.summary_paragraphs = summary_paragraphs
        row.pdf_url = pdf_url
        await self._s.flush()
        await self._s.refresh(row)
        return row

    # ── Experience ────────────────────────────────────────────────────────────

    async def list_experience(self) -> list[ResumeExperience]:
        stmt = select(ResumeExperience).order_by(ResumeExperience.sort_order)
        return list((await self._s.execute(stmt)).scalars())

    async def get_experience(self, id: uuid.UUID) -> ResumeExperience | None:
        return await self._s.get(ResumeExperience, id)

    async def create_experience(
        self,
        *,
        role: str,
        context: str,
        period: str,
        highlights: list[str],
    ) -> ResumeExperience:
        max_stmt = select(func.max(ResumeExperience.sort_order))
        max_order = (await self._s.execute(max_stmt)).scalar_one_or_none() or -1
        row = ResumeExperience(
            role=role,
            context=context,
            period=period,
            highlights=highlights,
            sort_order=max_order + 1,
        )
        self._s.add(row)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def update_experience(
        self,
        row: ResumeExperience,
        *,
        role: str,
        context: str,
        period: str,
        highlights: list[str],
    ) -> ResumeExperience:
        row.role = role
        row.context = context
        row.period = period
        row.highlights = highlights
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def delete_experience(self, row: ResumeExperience) -> None:
        await self._s.delete(row)
        await self._s.flush()

    # ── Skill groups ──────────────────────────────────────────────────────────

    async def list_skill_groups(self) -> list[ResumeSkillGroup]:
        stmt = select(ResumeSkillGroup).order_by(ResumeSkillGroup.sort_order)
        return list((await self._s.execute(stmt)).scalars())

    async def get_skill_group(self, id: uuid.UUID) -> ResumeSkillGroup | None:
        return await self._s.get(ResumeSkillGroup, id)

    async def create_skill_group(
        self,
        *,
        group_name: str,
        skills: list[str],
    ) -> ResumeSkillGroup:
        max_stmt = select(func.max(ResumeSkillGroup.sort_order))
        max_order = (await self._s.execute(max_stmt)).scalar_one_or_none() or -1
        row = ResumeSkillGroup(
            group_name=group_name,
            skills=skills,
            sort_order=max_order + 1,
        )
        self._s.add(row)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def update_skill_group(
        self,
        row: ResumeSkillGroup,
        *,
        group_name: str,
        skills: list[str],
    ) -> ResumeSkillGroup:
        row.group_name = group_name
        row.skills = skills
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def delete_skill_group(self, row: ResumeSkillGroup) -> None:
        await self._s.delete(row)
        await self._s.flush()

    # ── Education ─────────────────────────────────────────────────────────────

    async def list_education(self) -> list[ResumeEducation]:
        stmt = select(ResumeEducation).order_by(ResumeEducation.sort_order)
        return list((await self._s.execute(stmt)).scalars())

    async def get_education(self, id: uuid.UUID) -> ResumeEducation | None:
        return await self._s.get(ResumeEducation, id)

    async def create_education(
        self,
        *,
        institution: str,
        degree: str,
        status: str,
        notes: str | None,
    ) -> ResumeEducation:
        max_stmt = select(func.max(ResumeEducation.sort_order))
        max_order = (await self._s.execute(max_stmt)).scalar_one_or_none() or -1
        row = ResumeEducation(
            institution=institution,
            degree=degree,
            status=status,
            notes=notes,
            sort_order=max_order + 1,
        )
        self._s.add(row)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def update_education(
        self,
        row: ResumeEducation,
        *,
        institution: str,
        degree: str,
        status: str,
        notes: str | None,
    ) -> ResumeEducation:
        row.institution = institution
        row.degree = degree
        row.status = status
        row.notes = notes
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def delete_education(self, row: ResumeEducation) -> None:
        await self._s.delete(row)
        await self._s.flush()

    # ── Certifications ────────────────────────────────────────────────────────

    async def list_certifications(self) -> list[ResumeCertification]:
        stmt = select(ResumeCertification).order_by(ResumeCertification.sort_order)
        return list((await self._s.execute(stmt)).scalars())

    async def get_certification(self, id: uuid.UUID) -> ResumeCertification | None:
        return await self._s.get(ResumeCertification, id)

    async def create_certification(
        self,
        *,
        title: str,
        provider: str,
        status: str,
    ) -> ResumeCertification:
        max_stmt = select(func.max(ResumeCertification.sort_order))
        max_order = (await self._s.execute(max_stmt)).scalar_one_or_none() or -1
        row = ResumeCertification(
            title=title,
            provider=provider,
            status=status,
            sort_order=max_order + 1,
        )
        self._s.add(row)
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def update_certification(
        self,
        row: ResumeCertification,
        *,
        title: str,
        provider: str,
        status: str,
    ) -> ResumeCertification:
        row.title = title
        row.provider = provider
        row.status = status
        await self._s.flush()
        await self._s.refresh(row)
        return row

    async def delete_certification(self, row: ResumeCertification) -> None:
        await self._s.delete(row)
        await self._s.flush()
