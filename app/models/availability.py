"""
Availability ORM model.

Singleton table — always exactly one row (id = 1), seeded by migration 0005.

Status values mirror the frontend AvailabilityStatus type:
  available   — open to new opportunities
  limited     — selective; reach out to discuss
  unavailable — not currently taking opportunities
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AvailabilityStatus(StrEnum):
    AVAILABLE   = "available"
    LIMITED     = "limited"
    UNAVAILABLE = "unavailable"


class Availability(Base):
    __tablename__ = "availability"

    # Fixed to 1 — the service always reads/writes WHERE id = 1.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AvailabilityStatus.AVAILABLE,
        server_default=AvailabilityStatus.AVAILABLE,
    )
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    notice_period_weeks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
