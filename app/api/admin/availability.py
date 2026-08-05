"""
Admin availability endpoint.

  GET /admin/api/availability — read current availability
  PUT /admin/api/availability — update availability
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import get_current_admin
from app.db.session import get_db
from app.schemas.admin.availability import AdminAvailabilityOut, AvailabilityUpdate
from app.services.availability_service import AvailabilityService

logger = logging.getLogger(__name__)
router = APIRouter()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else None


def _get_service(db: AsyncSession = Depends(get_db)) -> AvailabilityService:
    return AvailabilityService(db)


@router.get(
    "",
    response_model=AdminAvailabilityOut,
    summary="Get current availability (admin)",
)
async def get_availability(
    service: AvailabilityService = Depends(_get_service),
    _admin: str = Depends(get_current_admin),
) -> AdminAvailabilityOut:
    return await service.get_admin()


@router.put(
    "",
    response_model=AdminAvailabilityOut,
    summary="Update availability",
)
async def update_availability(
    payload: AvailabilityUpdate,
    request: Request,
    service: AvailabilityService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminAvailabilityOut:
    return await service.update(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )
