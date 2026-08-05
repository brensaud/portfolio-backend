"""
Public analytics endpoint.

  POST /api/v1/analytics/view — record an anonymous page view.

No authentication required. Rate-limited by the shared rate limiter.
Deduplication is handled in the service layer (same session+path within 30 min).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.analytics import PageViewCreate
from app.services.analytics_service import AnalyticsService

router = APIRouter()


def _get_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.post(
    "/analytics/view",
    status_code=204,
    summary="Record an anonymous page view",
)
async def record_view(
    payload: PageViewCreate,
    service: AnalyticsService = Depends(_get_service),
) -> None:
    await service.record_view(payload)
