"""
AuditRepository — append-only persistence for admin audit log entries.

Design constraints:
  • No update() or delete() methods are provided.  Audit logs are permanent.
  • metadata_ must never contain PII.  The caller is responsible for
    passing only safe, pre-validated dicts (see AuditMetadata types in
    app/schemas/admin/auth.py).
  • Writes are performed within the caller's transaction.  For mutation
    endpoints, the audit entry and the mutation commit together.  For
    pre-authentication events (login failure), a separate session is used.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AdminAuditLog

logger = logging.getLogger(__name__)


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def write(
        self,
        *,
        action: str,
        actor: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AdminAuditLog:
        """
        Persist one audit log entry.

        Does NOT commit — the caller controls the transaction boundary.
        For login events (which have no other mutation), the caller must
        explicitly commit.
        """
        entry = AdminAuditLog(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            # Serialise to JSON string for SQLite compatibility in tests;
            # on PostgreSQL this column is effectively text-stored JSON.
            metadata_=json.dumps(metadata) if metadata is not None else None,
            ip_address=ip_address,
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def get_recent(
        self,
        *,
        limit: int = 20,
        actor: str | None = None,
    ) -> list[AdminAuditLog]:
        """Return the most recent audit log entries, newest first."""
        stmt = (
            select(AdminAuditLog)
            .order_by(AdminAuditLog.created_at.desc())
            .limit(limit)
        )
        if actor is not None:
            stmt = stmt.where(AdminAuditLog.actor == actor)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_ips_for_action(
        self,
        *,
        action: str,
        actor: str,
        limit: int = 10,
    ) -> list[str]:
        """Return distinct IP addresses from recent entries matching action + actor."""
        stmt = (
            select(AdminAuditLog.ip_address)
            .where(AdminAuditLog.action == action)
            .where(AdminAuditLog.actor == actor)
            .where(AdminAuditLog.ip_address.isnot(None))
            .order_by(AdminAuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [row for row in result.scalars().all() if row]
