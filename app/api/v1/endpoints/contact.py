"""
Contact message endpoint.

POST /api/v1/contact/messages

Accepts a JSON contact form submission, validates it, persists it to
the database, and triggers an email notification.

Rate limited: 5 requests per IP per hour (Redis-backed; degrades
gracefully when Redis is unavailable).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import check_rate_limit
from app.db.session import get_db
from app.schemas.contact import ContactMessageCreate, ContactMessageResponse
from app.schemas.errors import ErrorResponse
from app.services.contact_service import ContactService
from app.services.email_service import AbstractEmailService, get_email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contact", tags=["contact"])

_SUCCESS_MESSAGE = "Your message has been received. I'll respond within 48 hours."


@router.post(
    "/messages",
    response_model=ContactMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a contact message",
    responses={
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Unexpected server error"},
    },
    dependencies=[Depends(check_rate_limit)],
)
async def submit_contact_message(
    payload: ContactMessageCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    email_service: AbstractEmailService = Depends(get_email_service),
) -> ContactMessageResponse:
    """
    Submit a new contact form message.

    - Validates all fields (name, email, subject, message).
    - Enforces rate limit: 5 submissions per IP per hour.
    - Persists to PostgreSQL.
    - Triggers an email notification (non-blocking on failure).
    - Returns a reference ID for the sender.
    """
    ip = _get_ip(request)
    ua = request.headers.get("User-Agent", "")[:500]

    try:
        service = ContactService(db, email_service)
        contact = await service.submit_message(
            payload,
            ip_address=ip,
            user_agent=ua or None,
        )
    except SQLAlchemyError:
        logger.exception("Database error during contact submission")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        ) from None

    reference_id = f"MSG-{str(contact.id)[:8].upper()}"
    return ContactMessageResponse(
        id=contact.id,
        message=_SUCCESS_MESSAGE,
        reference_id=reference_id,
    )


def _get_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None
