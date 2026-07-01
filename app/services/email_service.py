"""
Email notification service abstraction.

Design:
  • `AbstractEmailService` defines the interface via a Protocol.
  • `ConsoleEmailService` (default) logs notification details to stdout —
    zero external dependencies, works offline.
  • To switch to a real provider (Resend, SendGrid, AWS SES, SMTP):
    1. Create a new class that implements `AbstractEmailService`.
    2. Replace `ConsoleEmailService()` in the dependency factory below.
    3. Add the provider's SDK to pyproject.toml.

Nothing else in the codebase needs to change — the service layer and
endpoint both depend only on `AbstractEmailService`.
"""

from __future__ import annotations

import logging
from typing import Protocol

from app.models.contact import ContactMessage

logger = logging.getLogger(__name__)


class AbstractEmailService(Protocol):
    """Interface for email notification providers."""

    async def send_contact_notification(self, contact: ContactMessage) -> None:
        """Send a notification email about a new contact submission."""
        ...


class ConsoleEmailService:
    """
    Development email service — logs to console instead of sending email.

    Replace with a real implementation before going to production.
    """

    async def send_contact_notification(self, contact: ContactMessage) -> None:
        logger.info(
            "[EMAIL] New contact submission — from=%r subject=%r id=%s",
            contact.email,
            contact.subject,
            contact.id,
        )
        # In development, log a preview of the message (truncated for safety)
        preview = contact.message[:100] + ("…" if len(contact.message) > 100 else "")
        logger.debug("[EMAIL] Message preview: %s", preview)


def get_email_service() -> AbstractEmailService:
    """
    FastAPI dependency factory.

    Swap `ConsoleEmailService()` with your real provider here:

        from app.services.resend_email_service import ResendEmailService
        return ResendEmailService(api_key=settings.resend_api_key)
    """
    return ConsoleEmailService()
