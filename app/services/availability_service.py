"""
AvailabilityService — shared service for reading and updating availability.

Used by both the public endpoint (read-only) and the admin endpoint (read + update).
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.availability import Availability
from app.repositories.availability_repo import AvailabilityRepository
from app.repositories.audit_repo import AuditRepository
from app.schemas.availability import AvailabilityPublic
from app.schemas.admin.availability import AdminAvailabilityOut, AvailabilityUpdate

logger = logging.getLogger(__name__)

_ACTION_UPDATED = "admin.availability.updated"
_RESOURCE_TYPE  = "availability"
_SINGLETON_ID   = "1"


class AvailabilityService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo    = AvailabilityRepository(session)
        self._audit   = AuditRepository(session)

    async def get_public(self) -> AvailabilityPublic:
        """Return the current availability as a public schema."""
        row = await self._repo.get()
        if row is None:
            # Fallback: row was somehow missing — return safe defaults
            return AvailabilityPublic(
                status="available",
                available_from=None,
                message=None,
                notice_period_weeks=None,
            )
        return AvailabilityPublic.model_validate(row)

    async def get_admin(self) -> AdminAvailabilityOut:
        """Return the current availability as an admin schema (includes id + updated_at)."""
        row = await self._repo.get()
        if row is None:
            row = await self._repo.upsert(
                status="available",
                available_from=None,
                message=None,
                notice_period_weeks=None,
            )
            await self._session.commit()
        return AdminAvailabilityOut.model_validate(row)

    async def update(
        self,
        data: AvailabilityUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminAvailabilityOut:
        """Update availability and write audit log."""
        row = await self._repo.upsert(
            status=data.status,
            available_from=data.available_from,
            message=data.message,
            notice_period_weeks=data.notice_period_weeks,
        )
        await self._audit.write(
            action=_ACTION_UPDATED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=_SINGLETON_ID,
            metadata={"status": data.status},
            ip_address=ip_address,
        )
        await self._session.commit()
        logger.info("Admin updated availability status=%r actor=%s", data.status, actor)
        return AdminAvailabilityOut.model_validate(row)
