"""
AdminContactService — business logic for admin contact message management.

Responsibilities:
  1. List messages with pagination, filtering, and search.
  2. Fetch a single message (auto-transitions unread → read on view).
  3. Explicit status mutations: mark_read, mark_unread, archive.
  4. Hard delete with pre-delete audit log (same transaction).

Design constraints:
  • This service owns every transaction boundary (commit).
  • The repository only flushes.
  • Every state-changing operation writes an audit log entry in the same
    transaction as the mutation.  A mutation cannot succeed without an audit
    record, and an audit record cannot be orphaned by a failed mutation.
  • No PII is written to audit log metadata — only status strings and UUIDs.
  • Hard delete is approved by the existing audit log design (resource_id is a
    nullable string — audit entries survive row deletion by design).
    See app/models/audit_log.py for the explicit design note.
"""

from __future__ import annotations

import logging
import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import ContactStatus
from app.repositories.audit_repo import AuditRepository
from app.repositories.contact_repo import ContactRepository
from app.schemas.admin.contact import (
    AdminContactMessageDetail,
    AdminContactMessageSummary,
    ContactMessagesPage,
)

logger = logging.getLogger(__name__)

# ── Audit action catalog ──────────────────────────────────────────────────────
# Centralised here so callers never hardcode action strings.
_ACTION_VIEWED = "admin.contact_message.viewed"
_ACTION_MARKED_READ = "admin.contact_message.marked_read"
_ACTION_MARKED_UNREAD = "admin.contact_message.marked_unread"
_ACTION_ARCHIVED = "admin.contact_message.archived"
_ACTION_DELETED = "admin.contact_message.deleted"

_RESOURCE_TYPE = "contact_message"


class AdminContactService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = ContactRepository(session)
        self._audit = AuditRepository(session)

    # ── List ──────────────────────────────────────────────────────────────────

    async def list_messages(
        self,
        *,
        page: int,
        page_size: int,
        status: ContactStatus | None,
        search: str | None,
        sort_desc: bool,
    ) -> ContactMessagesPage:
        """
        Return a paginated, filtered list of contact messages.

        Does not mutate any state or write audit logs — listing is a read-only
        operation.  The caller is responsible for any caching strategy.
        """
        items, total = await self._repo.list_admin(
            page=page,
            page_size=page_size,
            status=status,
            search=search,
            sort_desc=sort_desc,
        )
        pages = math.ceil(total / page_size) if total > 0 else 0

        return ContactMessagesPage(
            # Explicitly validate each ORM instance into the summary schema.
            # from_attributes=True handles the conversion; being explicit here
            # satisfies mypy and documents the intent.
            items=[AdminContactMessageSummary.model_validate(m) for m in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    # ── Get detail ────────────────────────────────────────────────────────────

    async def get_message(
        self,
        message_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminContactMessageDetail:
        """
        Fetch a single message and automatically transition unread → read.

        The status transition and audit log are committed atomically.
        If the message is already read or archived the status is not changed,
        but a viewed audit entry is still written.

        Raises:
            LookupError — if the message does not exist.  The route layer
                          converts this to HTTP 404.
        """
        message = await self._repo.get_by_id(message_id)
        if message is None:
            raise LookupError(f"Contact message {message_id} not found.")

        # Auto-transition unread → read on first view.
        status_changed = False
        if message.status == ContactStatus.UNREAD:
            message = await self._repo.update_status(message, ContactStatus.READ)
            status_changed = True

        # Write audit log — always log viewed; also log marked_read if the
        # status transitioned so the audit trail is complete.
        await self._audit.write(
            action=_ACTION_VIEWED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(message_id),
            metadata={"status_after": message.status},
            ip_address=ip_address,
        )
        if status_changed:
            await self._audit.write(
                action=_ACTION_MARKED_READ,
                actor=actor,
                resource_type=_RESOURCE_TYPE,
                resource_id=str(message_id),
                metadata={"trigger": "auto_on_view"},
                ip_address=ip_address,
            )

        await self._session.commit()

        logger.info(
            "Admin viewed contact id=%s actor=%s status_changed=%s",
            message_id,
            actor,
            status_changed,
        )
        return AdminContactMessageDetail.model_validate(message)

    # ── Status mutations ──────────────────────────────────────────────────────

    async def mark_read(
        self,
        message_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminContactMessageDetail:
        """Explicitly mark a message as read regardless of its current status."""
        return await self._mutate_status(
            message_id,
            new_status=ContactStatus.READ,
            action=_ACTION_MARKED_READ,
            actor=actor,
            ip_address=ip_address,
        )

    async def mark_unread(
        self,
        message_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminContactMessageDetail:
        """Mark a message as unread (undo a previous read or archive)."""
        return await self._mutate_status(
            message_id,
            new_status=ContactStatus.UNREAD,
            action=_ACTION_MARKED_UNREAD,
            actor=actor,
            ip_address=ip_address,
        )

    async def archive_message(
        self,
        message_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminContactMessageDetail:
        """Archive a message.  Archived messages are hidden from the default list view."""
        return await self._mutate_status(
            message_id,
            new_status=ContactStatus.ARCHIVED,
            action=_ACTION_ARCHIVED,
            actor=actor,
            ip_address=ip_address,
        )

    async def _mutate_status(
        self,
        message_id: uuid.UUID,
        *,
        new_status: ContactStatus,
        action: str,
        actor: str,
        ip_address: str | None,
    ) -> AdminContactMessageDetail:
        """
        Shared implementation for all status-change mutations.

        Fetches the message, updates its status, writes the audit log, and
        commits everything in a single transaction.

        Raises:
            LookupError — message not found → caller converts to HTTP 404.
        """
        message = await self._repo.get_by_id(message_id)
        if message is None:
            raise LookupError(f"Contact message {message_id} not found.")

        previous_status = message.status
        message = await self._repo.update_status(message, new_status)

        await self._audit.write(
            action=action,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(message_id),
            # Only non-PII metadata: status transition strings.
            metadata={
                "status_before": previous_status,
                "status_after": new_status,
            },
            ip_address=ip_address,
        )

        await self._session.commit()

        logger.info(
            "Admin %s contact id=%s actor=%s %s→%s",
            action,
            message_id,
            actor,
            previous_status,
            new_status,
        )
        return AdminContactMessageDetail.model_validate(message)

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete_message(
        self,
        message_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> None:
        """
        Permanently delete a contact message.

        Hard delete is approved by the existing audit log architecture: the
        AdminAuditLog table uses nullable string resource_id (not a FK) so
        the audit entry survives deletion of the referenced row.

        The audit entry is written BEFORE the delete and committed in the same
        transaction.  A delete cannot succeed without a permanent audit record.

        Raises:
            LookupError — message not found → caller converts to HTTP 404.
        """
        message = await self._repo.get_by_id(message_id)
        if message is None:
            raise LookupError(f"Contact message {message_id} not found.")

        # Capture the status before deletion for the audit record.
        status_at_delete = message.status

        # Write audit log first — same transaction as the delete.
        await self._audit.write(
            action=_ACTION_DELETED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(message_id),
            metadata={"status_at_delete": status_at_delete},
            ip_address=ip_address,
        )

        await self._repo.delete(message)
        await self._session.commit()

        logger.info(
            "Admin deleted contact id=%s actor=%s",
            message_id,
            actor,
        )
