"""
ContactRepository — data access layer for contact messages.

Keeps all SQL/ORM logic isolated from the service and API layers.
Easy to swap the underlying store (e.g. migrate to a different DB)
without touching business logic.
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import ContactMessage
from app.schemas.contact import ContactMessageCreate

logger = logging.getLogger(__name__)


class ContactRepository:
    """Async repository for ContactMessage persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        data: ContactMessageCreate,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ContactMessage:
        """
        Persist a new contact message and return the saved ORM instance.

        Does NOT commit — the caller (service layer) is responsible for
        committing so the transaction boundary stays at the service level.
        """
        contact = ContactMessage(
            name=data.name,
            email=data.email,
            subject=data.subject,
            message=data.message,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._session.add(contact)
        await self._session.flush()   # assigns `id` without committing
        await self._session.refresh(contact)

        logger.debug(
            "ContactMessage created id=%s from=%s",
            contact.id,
            contact.email,
        )
        return contact
