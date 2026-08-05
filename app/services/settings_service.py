"""
SettingsService — business logic for site settings.

Used by both the public endpoint (read-only) and the admin endpoint (read + update).
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_repo import AuditRepository
from app.repositories.settings_repo import SettingsRepository
from app.schemas.admin.settings import AdminProfileOut, ProfileUpdate
from app.schemas.settings import ProfilePublic

logger = logging.getLogger(__name__)

_ACTION_UPDATED = "admin.settings.profile.updated"
_RESOURCE_TYPE  = "site_settings"
_RESOURCE_ID    = "profile"


class SettingsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo    = SettingsRepository(session)
        self._audit   = AuditRepository(session)

    async def get_public(self) -> ProfilePublic:
        """Return the current profile as a public schema."""
        data = await self._repo.get_profile()
        return ProfilePublic(**data)

    async def get_admin(self) -> AdminProfileOut:
        """Return the current profile as an admin schema."""
        data = await self._repo.get_profile()
        return AdminProfileOut(**data)

    async def update_profile(
        self,
        payload: ProfileUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminProfileOut:
        """Upsert all profile fields and write an audit log entry."""
        data = await self._repo.upsert_profile(payload.model_dump())
        await self._audit.write(
            action=_ACTION_UPDATED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=_RESOURCE_ID,
            metadata={"fields_updated": list(payload.model_dump().keys())},
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminProfileOut(**data)
