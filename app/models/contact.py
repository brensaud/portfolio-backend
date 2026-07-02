"""
ContactMessage ORM model.

Stores every inbound contact form submission.
`status` tracks the admin lifecycle: unread → read → archived.

Column notes:
  • id          — UUID primary key (CHAR(32) on SQLite in tests, UUID on PG)
  • ip_address  — optional; stored for spam analysis, max 45 chars (IPv6)
  • user_agent  — optional; first 500 chars of the raw UA string
  • created_at  — set by the DB on INSERT (server_default)
  • updated_at  — set by the DB on INSERT and updated on UPDATE

Status lifecycle (migration 0003 renamed the original values):
  unread   — newly received, not yet viewed by admin (was: "new")
  read     — admin has opened the message
  archived — admin has archived the message (soft-equivalent of dismissed)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContactStatus(StrEnum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ContactStatus.UNREAD,
        server_default=ContactStatus.UNREAD,
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<ContactMessage id={self.id} from={self.email!r} subject={self.subject!r}>"
