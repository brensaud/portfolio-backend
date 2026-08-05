"""Business logic for privacy-first analytics."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics_repo import PageViewRepository
from app.schemas.analytics import PageViewCreate
from app.schemas.admin.analytics import (
    AnalyticsCountriesOut,
    AnalyticsPagesOut,
    AnalyticsReferrersOut,
    AnalyticsSummaryOut,
    CountryBreakdown,
    DailyViews,
    PageBreakdown,
    ReferrerBreakdown,
)

_VALID_PERIODS = {"7d", "30d", "all"}


def _validate_period(period: str) -> str:
    return period if period in _VALID_PERIODS else "7d"


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = PageViewRepository(db)

    # ── public ────────────────────────────────────────────────────────────────

    async def record_view(self, payload: PageViewCreate) -> None:
        """Record a page view (deduplication handled in the repository)."""
        # Sanitise path: keep only the path portion, truncate
        path = payload.path[:500].strip() or "/"
        referrer = (payload.referrer or "").strip()[:500] or None

        await self._repo.record(
            path=path,
            session_id=payload.session_id[:64],
            referrer=referrer,
            country=None,  # geolocation deferred
        )
        await self._db.commit()

    # ── admin reads ───────────────────────────────────────────────────────────

    async def get_summary(self, period: str = "7d") -> AnalyticsSummaryOut:
        period = _validate_period(period)
        total = await self._repo.total_views(period)
        unique = await self._repo.unique_sessions(period)
        daily_raw = await self._repo.daily_views(period)
        pages = await self._repo.top_pages(period, limit=1)
        top_page = pages[0]["path"] if pages else None
        return AnalyticsSummaryOut(
            period=period,
            total_views=total,
            unique_sessions=unique,
            top_page=top_page,
            daily=[DailyViews(**d) for d in daily_raw],
        )

    async def get_pages(self, period: str = "7d", limit: int = 10) -> AnalyticsPagesOut:
        period = _validate_period(period)
        rows = await self._repo.top_pages(period, limit=min(limit, 50))
        return AnalyticsPagesOut(
            period=period,
            pages=[PageBreakdown(**r) for r in rows],
        )

    async def get_referrers(self, period: str = "7d", limit: int = 10) -> AnalyticsReferrersOut:
        period = _validate_period(period)
        rows = await self._repo.top_referrers(period, limit=min(limit, 50))
        return AnalyticsReferrersOut(
            period=period,
            referrers=[ReferrerBreakdown(**r) for r in rows],
        )

    async def get_countries(self, period: str = "7d", limit: int = 10) -> AnalyticsCountriesOut:
        period = _validate_period(period)
        rows = await self._repo.top_countries(period, limit=min(limit, 50))
        return AnalyticsCountriesOut(
            period=period,
            countries=[CountryBreakdown(**r) for r in rows],
        )
