"""
Public availability endpoint.

  GET /api/v1/availability — current availability status (no auth required)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.availability import AvailabilityPublic
from app.services.availability_service import AvailabilityService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/availability", tags=["availability"])


def _get_service(db: AsyncSession = Depends(get_db)) -> AvailabilityService:
    return AvailabilityService(db)


@router.get(
    "",
    response_model=AvailabilityPublic,
    summary="Get current availability",
)
async def get_availability(
    service: AvailabilityService = Depends(_get_service),
) -> AvailabilityPublic:
    """Return the current open-to-work status and associated metadata."""
    return await service.get_public()
