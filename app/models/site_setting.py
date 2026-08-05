"""
SiteSetting ORM model.

Key-value store for site-wide settings (profile, social links, etc.).
Each setting is one row with a text key and an optional text value.

Well-known key prefix:
  profile.*  — name, role, tagline, bio, github, linkedin, email, twitter_handle
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SiteSetting(Base):
    __tablename__ = "site_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
