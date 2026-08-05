"""
AvailabilityRepository — data access layer for the singleton availability row.

The availability table always has exactly one row (id = 1), seeded by migration 0005.

Methods:
  get()    — fetch the single row; returns None if row is missing (shouldn't happen)
  upsert() — update the single row; inserts with id=1 if somehow missing
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.availability import Availability

logger = logging.getLogger(__name__)

_SINGLETON_ID = 1


class AvailabilityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self) -> Availability | None:
        """Return the singleton availability row."""
        stmt = select(Availability).where(Availability.id == _SINGLETON_ID)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        *,
        status: str,
        available_from: object | None,
        message: str | None,
        notice_period_weeks: int | None,
    ) -> Availability:
        """Update the singleton row, creating it with id=1 if absent. Does NOT commit."""
        row = await self.get()
        if row is None:
            row = Availability(id=_SINGLETON_ID, status=status)
            self._session.add(row)

        row.status = status
        row.available_from = available_from
        row.message = message
        row.notice_period_weeks = notice_period_weeks

        await self._session.flush()
        await self._session.refresh(row)
        return row
