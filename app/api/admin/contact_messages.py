"""
Admin contact messages endpoints.

All routes are mounted under /admin/api/contact-messages.
The get_current_admin dependency is applied at the router level in
app/api/admin/router.py — every endpoint here is protected automatically.

Endpoint summary:
  GET    /admin/api/contact-messages            — paginated list
  GET    /admin/api/contact-messages/{id}       — detail (auto marks unread→read)
  PATCH  /admin/api/contact-messages/{id}/read      — mark as read
  PATCH  /admin/api/contact-messages/{id}/unread    — mark as unread
  PATCH  /admin/api/contact-messages/{id}/archive   — archive
  DELETE /admin/api/contact-messages/{id}           — hard delete

Thin route layer — no business logic here.  All logic lives in
AdminContactService.  Routes are responsible only for:
  • Declaring the HTTP interface (method, path, status codes, response model).
  • Extracting HTTP-level concerns (client IP, query params).
  • Translating service exceptions to HTTP responses.
  • Injecting dependencies.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import get_current_admin
from app.db.session import get_db
from app.models.contact import ContactStatus
from app.schemas.admin.contact import (
    AdminContactMessageDetail,
    ContactMessagesPage,
)
from app.schemas.errors import ErrorResponse
from app.services.admin_contact_service import AdminContactService

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Sort literal type ─────────────────────────────────────────────────────────

SortOrder = Literal["created_at_desc", "created_at_asc"]

# ── Shared responses ──────────────────────────────────────────────────────────
# Typed explicitly so mypy accepts **-spreading into FastAPI's responses= dict.
# FastAPI's responses parameter is Dict[Union[int, str], Dict[str, Any]].

_Responses = dict[int | str, dict[str, Any]]

_NOT_FOUND: _Responses = {404: {"model": ErrorResponse, "description": "Message not found"}}
_UNAUTH: _Responses = {401: {"model": ErrorResponse, "description": "Authentication required"}}


def _client_ip(request: Request) -> str | None:
    """Extract the real client IP (rightmost X-Forwarded-For entry)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else None


def _get_service(db: AsyncSession = Depends(get_db)) -> AdminContactService:
    """FastAPI dependency — constructs the service with the request-scoped session."""
    return AdminContactService(db)


# ── List ──────────────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=ContactMessagesPage,
    summary="List contact messages",
    responses={**_UNAUTH},
)
async def list_contact_messages(
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Items per page (max 100)",
    ),
    status: ContactStatus | None = Query(
        default=None,
        description="Filter by status: unread, read, or archived",
    ),
    search: str | None = Query(
        default=None,
        max_length=200,
        description="Search name, email, or subject (case-insensitive)",
    ),
    sort: SortOrder = Query(
        default="created_at_desc",
        description="Sort order: created_at_desc (newest first) or created_at_asc",
    ),
    service: AdminContactService = Depends(_get_service),
    # Auth is enforced by the router-level get_current_admin dependency in
    # admin/router.py.  The email is not needed here — no audit log on list.
) -> ContactMessagesPage:
    """
    Return a paginated list of contact messages.

    Supports filtering by status, free-text search across name/email/subject,
    and ascending/descending sort by creation date.

    The `message` body is excluded from list items to reduce PII surface area.
    Use GET /{id} to retrieve the full message content.
    """
    # Strip and normalise the search term.  An empty string after stripping is
    # treated as no search filter.
    clean_search = search.strip() if search else None
    clean_search = clean_search or None

    result = await service.list_messages(
        page=page,
        page_size=page_size,
        status=status,
        search=clean_search,
        sort_desc=(sort == "created_at_desc"),
    )
    return result


# ── Detail ────────────────────────────────────────────────────────────────────


@router.get(
    "/{message_id}",
    response_model=AdminContactMessageDetail,
    summary="Get contact message detail",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def get_contact_message(
    message_id: uuid.UUID,
    request: Request,
    service: AdminContactService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminContactMessageDetail:
    """
    Fetch a single message by ID.

    Side effect: automatically transitions the status from `unread` to `read`
    on first view.  Messages already in `read` or `archived` state are
    unaffected.  Both actions (viewed + marked_read) are audit logged.
    """
    try:
        return await service.get_message(
            message_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found.",
        ) from None


# ── Status mutations ──────────────────────────────────────────────────────────


@router.patch(
    "/{message_id}/read",
    response_model=AdminContactMessageDetail,
    summary="Mark message as read",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def mark_message_read(
    message_id: uuid.UUID,
    request: Request,
    service: AdminContactService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminContactMessageDetail:
    """Explicitly mark a contact message as read."""
    try:
        return await service.mark_read(
            message_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found.",
        ) from None


@router.patch(
    "/{message_id}/unread",
    response_model=AdminContactMessageDetail,
    summary="Mark message as unread",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def mark_message_unread(
    message_id: uuid.UUID,
    request: Request,
    service: AdminContactService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminContactMessageDetail:
    """Mark a message as unread (undo a previous read or archive)."""
    try:
        return await service.mark_unread(
            message_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found.",
        ) from None


@router.patch(
    "/{message_id}/archive",
    response_model=AdminContactMessageDetail,
    summary="Archive a message",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def archive_contact_message(
    message_id: uuid.UUID,
    request: Request,
    service: AdminContactService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminContactMessageDetail:
    """
    Archive a contact message.

    Archived messages are excluded from the default list view (use
    status=archived to retrieve them).  This is the recommended alternative
    to deletion for messages that should be retained.
    """
    try:
        return await service.archive_message(
            message_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found.",
        ) from None


# ── Delete ────────────────────────────────────────────────────────────────────


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete a message",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def delete_contact_message(
    message_id: uuid.UUID,
    request: Request,
    service: AdminContactService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> None:
    """
    Permanently delete a contact message.

    This is a hard delete — the row is removed from the database.  An audit
    log entry is written in the same transaction before deletion so the action
    is permanently recorded even though the message row no longer exists.

    Use archive instead if you want a reversible action.
    """
    try:
        await service.delete_message(
            message_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact message not found.",
        ) from None
