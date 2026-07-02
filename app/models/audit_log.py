"""
AdminAuditLog ORM model.

Append-only record of all significant admin actions.

Design principles:
  • No UPDATE or DELETE is ever issued against this table — the repository
    layer enforces this by exposing only a write() method.
  • metadata JSONB must never contain PII (email addresses, message bodies,
    names, passwords, tokens).  The typed AuditMetadata schemas in
    app/schemas/admin/auth.py enforce this structurally.
  • The actor column stores the admin email or the string "system".
  • resource_type / resource_id are nullable strings (not FK constraints)
    so audit entries survive deletion of the referenced row.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Who performed the action ("admin@example.com" or "system")
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    # Action key from the defined action catalog (e.g. "admin.login_success")
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # Resource type this action affected (e.g. "contact_message")
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Stringified UUID of the affected resource
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Non-PII context about the action.  See AuditMetadata types for allowed shapes.
    # SQLite (used in tests) does not support JSONB — stored as Text there.
    metadata_: Mapped[str | None] = mapped_column("metadata", Text, nullable=True)
    # Client IP address (stored separately, never in metadata_)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
