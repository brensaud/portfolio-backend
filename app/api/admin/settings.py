"""
Admin settings endpoints.

  GET /admin/api/settings/profile — read current profile
  PUT /admin/api/settings/profile — update profile
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import get_current_admin
from app.db.session import get_db
from app.schemas.admin.settings import AdminProfileOut, ProfileUpdate
from app.services.settings_service import SettingsService

logger = logging.getLogger(__name__)
router = APIRouter()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else None


def _get_service(db: AsyncSession = Depends(get_db)) -> SettingsService:
    return SettingsService(db)


@router.get(
    "/profile",
    response_model=AdminProfileOut,
    summary="Get profile settings (admin)",
)
async def get_profile(
    service: SettingsService = Depends(_get_service),
    _admin: str = Depends(get_current_admin),
) -> AdminProfileOut:
    return await service.get_admin()


@router.put(
    "/profile",
    response_model=AdminProfileOut,
    summary="Update profile settings",
)
async def update_profile(
    payload: ProfileUpdate,
    request: Request,
    service: SettingsService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminProfileOut:
    return await service.update_profile(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )
