"""
ContactService — business logic for contact form submissions.

Responsibilities:
  1. Delegate persistence to ContactRepository.
  2. Commit the database transaction.
  3. Trigger the email notification (fire-and-forget on error).
  4. Return the saved ContactMessage to the caller.

The service owns the transaction boundary; the repository only flushes.
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import ContactMessage
from app.repositories.contact_repo import ContactRepository
from app.schemas.contact import ContactMessageCreate
from app.services.email_service import AbstractEmailService

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(
        self,
        session: AsyncSession,
        email_service: AbstractEmailService,
    ) -> None:
        self._repo = ContactRepository(session)
        self._session = session
        self._email = email_service

    async def submit_message(
        self,
        data: ContactMessageCreate,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ContactMessage:
        """
        Validate, persist, and notify about a new contact submission.

        Raises:
            sqlalchemy.exc.SQLAlchemyError — propagated to the endpoint
                where a 500 handler converts it to a safe error response.
        """
        logger.info(
            "Contact submission received from=%r subject=%r ip=%s",
            data.email,
            data.subject,
            ip_address or "unknown",
        )

        # Persist
        contact = await self._repo.create(
            data,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._session.commit()

        logger.info("Contact submission stored id=%s", contact.id)

        # Notify — errors here must not fail the request
        try:
            await self._email.send_contact_notification(contact)
        except Exception:
            logger.exception(
                "Email notification failed for contact id=%s (non-fatal)",
                contact.id,
            )

        return contact
