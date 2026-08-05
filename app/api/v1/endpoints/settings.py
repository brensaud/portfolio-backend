"""
Public settings endpoint.

  GET /api/v1/settings/profile — current profile data (no auth required)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.settings import ProfilePublic
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])


def _get_service(db: AsyncSession = Depends(get_db)) -> SettingsService:
    return SettingsService(db)


@router.get(
    "/profile",
    response_model=ProfilePublic,
    summary="Get public profile",
)
async def get_profile(
    service: SettingsService = Depends(_get_service),
) -> ProfilePublic:
    """Return the site owner's public profile (name, role, bio, social links)."""
    return await service.get_public()
