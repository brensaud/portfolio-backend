"""
SettingsRepository — data access for the key-value site_settings table.

All profile fields are stored with the prefix "profile." (e.g. "profile.name").

Methods:
  get_profile()     — returns all profile fields as a flat dict (field → value)
  upsert_profile()  — bulk-upsert all profile fields; does NOT commit
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site_setting import SiteSetting

logger = logging.getLogger(__name__)

_PROFILE_FIELDS = (
    "name",
    "role",
    "tagline",
    "bio",
    "github",
    "linkedin",
    "email",
    "twitter_handle",
)

# Safe defaults so the public endpoint always returns valid data.
_DEFAULTS: dict[str, str | None] = {
    "name":           "Bren Saud",
    "role":           "Python Backend Engineer",
    "tagline":        "Building production-grade backend systems and AI products.",
    "bio":            None,
    "github":         "https://github.com/brensaud",
    "linkedin":       None,
    "email":          None,
    "twitter_handle": None,
}


class SettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_profile(self) -> dict[str, str | None]:
        """Return all profile fields as {field: value}, using defaults for missing keys."""
        keys = [f"profile.{f}" for f in _PROFILE_FIELDS]
        stmt = select(SiteSetting).where(SiteSetting.key.in_(keys))
        result = await self._session.execute(stmt)
        stored = {row.key.removeprefix("profile."): row.value for row in result.scalars()}
        return {field: stored.get(field, _DEFAULTS[field]) for field in _PROFILE_FIELDS}

    async def upsert_profile(self, data: dict[str, str | None]) -> dict[str, str | None]:
        """Upsert profile fields. Portable with both PostgreSQL and SQLite. Does NOT commit."""
        for field, value in data.items():
            key = f"profile.{field}"
            stmt = select(SiteSetting).where(SiteSetting.key == key)
            result = await self._session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                self._session.add(SiteSetting(key=key, value=value))
            else:
                row.value = value
        await self._session.flush()
        return await self.get_profile()
