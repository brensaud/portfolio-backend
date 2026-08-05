"""
Admin analytics endpoints.

  GET /admin/api/analytics/summary    — total views, unique sessions, daily chart
  GET /admin/api/analytics/pages      — top pages breakdown
  GET /admin/api/analytics/referrers  — top referrers
  GET /admin/api/analytics/countries  — top countries

All endpoints accept an optional `period` query param: 7d | 30d | all (default: 7d).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import get_current_admin
from app.db.session import get_db
from app.schemas.admin.analytics import (
    AnalyticsCountriesOut,
    AnalyticsPagesOut,
    AnalyticsReferrersOut,
    AnalyticsSummaryOut,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()
_protected = APIRouter(dependencies=[Depends(get_current_admin)])


def _get_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@_protected.get(
    "/summary",
    response_model=AnalyticsSummaryOut,
    summary="Analytics summary — views, sessions, daily chart",
)
async def get_summary(
    period: str = Query(default="7d"),
    service: AnalyticsService = Depends(_get_service),
) -> AnalyticsSummaryOut:
    return await service.get_summary(period)


@_protected.get(
    "/pages",
    response_model=AnalyticsPagesOut,
    summary="Top pages breakdown",
)
async def get_pages(
    period: str = Query(default="7d"),
    limit: int = Query(default=10, ge=1, le=50),
    service: AnalyticsService = Depends(_get_service),
) -> AnalyticsPagesOut:
    return await service.get_pages(period, limit)


@_protected.get(
    "/referrers",
    response_model=AnalyticsReferrersOut,
    summary="Top referrers breakdown",
)
async def get_referrers(
    period: str = Query(default="7d"),
    limit: int = Query(default=10, ge=1, le=50),
    service: AnalyticsService = Depends(_get_service),
) -> AnalyticsReferrersOut:
    return await service.get_referrers(period, limit)


@_protected.get(
    "/countries",
    response_model=AnalyticsCountriesOut,
    summary="Top countries breakdown",
)
async def get_countries(
    period: str = Query(default="7d"),
    limit: int = Query(default=10, ge=1, le=50),
    service: AnalyticsService = Depends(_get_service),
) -> AnalyticsCountriesOut:
    return await service.get_countries(period, limit)


router.include_router(_protected)
