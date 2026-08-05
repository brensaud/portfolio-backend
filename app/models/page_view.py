"""
PageView ORM model — privacy-first analytics.

Design decisions:
  - IP address is NEVER stored; country is derived from IP in the service layer
    and only the 2-letter code is persisted (or null if lookup fails/deferred)
  - session_id is an anonymous random UUID generated in the browser (sessionStorage)
    and is not linkable to a real identity
  - Deduplication: the service skips recording if the same session_id + path
    was seen within the last 30 minutes, preventing refresh spam
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PageView(Base):
    __tablename__ = "page_views"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # URL path only (e.g. "/work/interviewpilot-ai") — no query string, no host
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    # HTTP Referer header, truncated to 500 chars; null if not sent
    referrer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # ISO 3166-1 alpha-2 country code derived from IP; IP is discarded immediately
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    # Anonymous random UUID from browser sessionStorage — never linkable to a person
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_page_views_created_at", "created_at"),
        Index("ix_page_views_path", "path"),
        Index("ix_page_views_session_path", "session_id", "path", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<PageView path={self.path!r} session={self.session_id[:8]}…>"
