"""PageView data-access layer."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.page_view import PageView


_DEDUP_WINDOW_MINUTES = 30


class PageViewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── write ─────────────────────────────────────────────────────────────────

    async def record(
        self,
        *,
        path: str,
        session_id: str,
        referrer: str | None,
        country: str | None,
    ) -> PageView | None:
        """Insert a page view, skipping if the same session saw this path recently."""
        cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=_DEDUP_WINDOW_MINUTES)
        existing = await self._db.execute(
            select(PageView.id).where(
                PageView.session_id == session_id,
                PageView.path == path,
                PageView.created_at >= cutoff,
            ).limit(1)
        )
        if existing.scalar_one_or_none() is not None:
            return None  # duplicate within dedup window

        pv = PageView(
            id=uuid.uuid4(),
            path=path,
            session_id=session_id,
            referrer=referrer,
            country=country,
        )
        self._db.add(pv)
        await self._db.flush()
        return pv

    # ── aggregate reads ───────────────────────────────────────────────────────

    def _since(self, period: str) -> datetime | None:
        """Convert a period string to an absolute UTC cutoff (or None for all time)."""
        if period == "7d":
            return datetime.now(tz=timezone.utc) - timedelta(days=7)
        if period == "30d":
            return datetime.now(tz=timezone.utc) - timedelta(days=30)
        return None  # all time

    async def total_views(self, period: str) -> int:
        cutoff = self._since(period)
        q = select(func.count(PageView.id))
        if cutoff:
            q = q.where(PageView.created_at >= cutoff)
        result = await self._db.execute(q)
        return result.scalar_one() or 0

    async def unique_sessions(self, period: str) -> int:
        cutoff = self._since(period)
        q = select(func.count(func.distinct(PageView.session_id)))
        if cutoff:
            q = q.where(PageView.created_at >= cutoff)
        result = await self._db.execute(q)
        return result.scalar_one() or 0

    async def top_pages(self, period: str, limit: int = 10) -> list[dict]:
        cutoff = self._since(period)
        q = (
            select(PageView.path, func.count(PageView.id).label("views"))
            .group_by(PageView.path)
            .order_by(desc("views"))
            .limit(limit)
        )
        if cutoff:
            q = q.where(PageView.created_at >= cutoff)
        result = await self._db.execute(q)
        return [{"path": r.path, "views": r.views} for r in result.all()]

    async def top_referrers(self, period: str, limit: int = 10) -> list[dict]:
        cutoff = self._since(period)
        q = (
            select(PageView.referrer, func.count(PageView.id).label("views"))
            .where(PageView.referrer.is_not(None))
            .group_by(PageView.referrer)
            .order_by(desc("views"))
            .limit(limit)
        )
        if cutoff:
            q = q.where(PageView.created_at >= cutoff)
        result = await self._db.execute(q)
        return [{"referrer": r.referrer, "views": r.views} for r in result.all()]

    async def top_countries(self, period: str, limit: int = 10) -> list[dict]:
        cutoff = self._since(period)
        q = (
            select(PageView.country, func.count(PageView.id).label("views"))
            .where(PageView.country.is_not(None))
            .group_by(PageView.country)
            .order_by(desc("views"))
            .limit(limit)
        )
        if cutoff:
            q = q.where(PageView.created_at >= cutoff)
        result = await self._db.execute(q)
        return [{"country": r.country, "views": r.views} for r in result.all()]

    async def daily_views(self, period: str) -> list[dict]:
        """Return views per calendar day for the given period (ascending)."""
        cutoff = self._since(period) or (datetime.now(tz=timezone.utc) - timedelta(days=30))
        # func.date() works on both PostgreSQL and SQLite
        q = (
            select(
                func.date(PageView.created_at).label("date"),
                func.count(PageView.id).label("views"),
            )
            .where(PageView.created_at >= cutoff)
            .group_by(func.date(PageView.created_at))
            .order_by(func.date(PageView.created_at))
        )
        result = await self._db.execute(q)
        return [{"date": str(r.date), "views": r.views} for r in result.all()]
