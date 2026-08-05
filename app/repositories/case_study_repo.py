"""CaseStudy data-access layer."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case_study import CaseStudy, CaseStudyStatus


class CaseStudyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── reads ─────────────────────────────────────────────────────────────────

    async def list_all(self) -> list[CaseStudy]:
        result = await self._db.execute(
            select(CaseStudy).order_by(CaseStudy.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> CaseStudy | None:
        result = await self._db.execute(
            select(CaseStudy).where(CaseStudy.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_published_by_slug(self, slug: str) -> CaseStudy | None:
        result = await self._db.execute(
            select(CaseStudy).where(
                CaseStudy.slug == slug,
                CaseStudy.status == CaseStudyStatus.PUBLISHED,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, id: uuid.UUID) -> CaseStudy | None:
        result = await self._db.execute(
            select(CaseStudy).where(CaseStudy.id == id)
        )
        return result.scalar_one_or_none()

    # ── writes ────────────────────────────────────────────────────────────────

    async def create(
        self,
        *,
        slug: str,
        disclaimer: str | None = None,
        content: dict | None = None,
    ) -> CaseStudy:
        cs = CaseStudy(
            id=uuid.uuid4(),
            slug=slug,
            status=CaseStudyStatus.DRAFT,
            disclaimer=disclaimer,
            content=content or {},
        )
        self._db.add(cs)
        await self._db.flush()
        return cs

    async def update(
        self,
        cs: CaseStudy,
        *,
        slug: str | None = None,
        disclaimer: str | None = None,
        content: dict | None = None,
    ) -> CaseStudy:
        if slug is not None:
            cs.slug = slug
        if disclaimer is not None:
            cs.disclaimer = disclaimer
        if content is not None:
            cs.content = content
        await self._db.flush()
        return cs

    async def publish(self, cs: CaseStudy) -> CaseStudy:
        cs.status = CaseStudyStatus.PUBLISHED
        if cs.published_at is None:
            cs.published_at = datetime.now(tz=timezone.utc)
        await self._db.flush()
        return cs

    async def unpublish(self, cs: CaseStudy) -> CaseStudy:
        cs.status = CaseStudyStatus.DRAFT
        await self._db.flush()
        return cs

    async def delete(self, cs: CaseStudy) -> None:
        await self._db.delete(cs)
        await self._db.flush()
