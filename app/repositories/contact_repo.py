"""
ContactRepository — data access layer for contact messages.

Keeps all SQL/ORM logic isolated from the service and API layers.
Easy to swap the underlying store (e.g. migrate to a different DB)
without touching business logic.

Public-facing methods:
  create()          — persist a new submission (used by public contact endpoint)

Admin methods (Sprint 2):
  list_admin()      — paginated, filtered, searchable list
  get_by_id()       — single message lookup
  update_status()   — change the status field
  delete()          — hard delete (audit log entry written by the caller first)
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import ContactMessage, ContactStatus
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
        await self._session.flush()  # assigns `id` without committing
        await self._session.refresh(contact)

        logger.debug(
            "ContactMessage created id=%s from=%s",
            contact.id,
            contact.email,
        )
        return contact

    # ── Admin methods ─────────────────────────────────────────────────────────

    async def list_admin(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: ContactStatus | None = None,
        search: str | None = None,
        sort_desc: bool = True,
    ) -> tuple[list[ContactMessage], int]:
        """
        Return a paginated list of contact messages for admin consumption.

        Args:
            page:       1-based page number.
            page_size:  Number of items per page (caller enforces 1–100 cap).
            status:     Optional status filter.  None = all statuses.
            search:     Optional search string.  Applied as case-insensitive
                        substring match on name, email, and subject.
                        The caller is responsible for stripping the value.
            sort_desc:  True = newest first (default); False = oldest first.

        Returns:
            A 2-tuple of (items, total) where total reflects the unfiltered count
            matching the current filters (used for pagination metadata).
        """
        base_stmt = select(ContactMessage)

        # ── Filters ───────────────────────────────────────────────────────────
        if status is not None:
            base_stmt = base_stmt.where(ContactMessage.status == status)

        if search:
            # Parameterised ILIKE — SQLAlchemy passes this as a bound parameter,
            # preventing SQL injection regardless of the search string content.
            pattern = f"%{search}%"
            base_stmt = base_stmt.where(
                or_(
                    ContactMessage.name.ilike(pattern),
                    ContactMessage.email.ilike(pattern),
                    ContactMessage.subject.ilike(pattern),
                )
            )

        # ── Total count (same filters, no pagination) ─────────────────────────
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        # ── Ordering + pagination ─────────────────────────────────────────────
        order_col = (
            ContactMessage.created_at.desc() if sort_desc else ContactMessage.created_at.asc()
        )
        page_stmt = base_stmt.order_by(order_col).offset((page - 1) * page_size).limit(page_size)

        result = await self._session.execute(page_stmt)
        items = list(result.scalars().all())

        logger.debug(
            "list_admin page=%d page_size=%d status=%s search=%r → %d/%d",
            page,
            page_size,
            status,
            search,
            len(items),
            total,
        )
        return items, total

    async def get_by_id(self, message_id: uuid.UUID) -> ContactMessage | None:
        """Return a single ContactMessage by primary key, or None if not found."""
        stmt = select(ContactMessage).where(ContactMessage.id == message_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        message: ContactMessage,
        status: ContactStatus,
    ) -> ContactMessage:
        """
        Set a new status on an already-loaded ContactMessage instance.

        Does NOT commit — the service layer owns the transaction boundary.
        The ORM `onupdate` hook on `updated_at` fires automatically on flush.
        """
        message.status = status
        await self._session.flush()
        await self._session.refresh(message)

        logger.debug(
            "ContactMessage id=%s status updated → %s",
            message.id,
            status,
        )
        return message

    async def delete(self, message: ContactMessage) -> None:
        """
        Hard-delete a ContactMessage row.

        Security note: the caller (AdminContactService) MUST write an audit log
        entry within the same transaction BEFORE calling this method.  The audit
        entry uses nullable resource_id strings so it survives the row deletion.

        Does NOT commit — the service layer owns the transaction boundary.
        """
        await self._session.delete(message)
        await self._session.flush()

        logger.debug("ContactMessage id=%s deleted", message.id)
