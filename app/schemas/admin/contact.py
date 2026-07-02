"""
Admin-facing Pydantic schemas for contact message management.

Response design decisions:
  • AdminContactMessageSummary — used in the list endpoint.  Omits `message`
    body, `ip_address`, and `user_agent` to minimise PII exposure on list views.
  • AdminContactMessageDetail — used in the single-message and mutation
    endpoints.  Includes the full message body and metadata fields.
  • ContactMessagesPage — pagination envelope; mirrors the pattern used by
    other list endpoints across the project.

All schemas use ConfigDict(extra="forbid") to prevent parameter pollution
and accidental field inclusion from ORM instances.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminContactMessageSummary(BaseModel):
    """
    Compact representation returned in list responses.

    The `message` body is intentionally excluded — it may be lengthy and
    exposing it on every list row increases unnecessary PII surface area.
    Full content is available via the detail endpoint.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    name: str
    email: str
    subject: str
    status: str
    created_at: datetime
    updated_at: datetime


class AdminContactMessageDetail(BaseModel):
    """
    Full representation returned when a specific message is requested.

    Includes the message body and optional metadata (ip_address, user_agent).
    Returned by: GET /{id}, PATCH /{id}/read, PATCH /{id}/unread,
                 PATCH /{id}/archive.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    name: str
    email: str
    subject: str
    message: str
    status: str
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    updated_at: datetime


class ContactMessagesPage(BaseModel):
    """
    Pagination envelope for the contact messages list endpoint.

    `pages` is derived server-side so the client does not need to calculate it.
    `total` always reflects the full count matching the current filters.
    """

    model_config = ConfigDict(extra="forbid")

    items: list[AdminContactMessageSummary]
    total: int = Field(ge=0, description="Total messages matching current filters")
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0, description="Total pages — 0 when total is 0")
