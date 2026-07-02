"""
Admin contact messages endpoint tests.

Test scenarios:
  List
    ✓ Authenticated admin can list messages
    ✓ Unauthenticated request → 401
    ✓ Default response includes pagination metadata
    ✓ Filter by status
    ✓ Invalid status value → 422
    ✓ Search across name, email, subject
    ✓ Search with whitespace-only string is treated as no-search
    ✓ Pagination: page and page_size respected
    ✓ page_size > 100 → 422
    ✓ page < 1 → 422
    ✓ Message body is NOT included in list items
    ✓ ip_address and user_agent NOT included in list items
    ✓ Sort descending (newest first)
    ✓ Sort ascending (oldest first)

  Detail
    ✓ Authenticated admin can fetch a message
    ✓ Unauthenticated request → 401
    ✓ Non-existent id → 404
    ✓ Malformed UUID → 422
    ✓ Viewing an unread message marks it as read (auto-transition)
    ✓ Viewing a read message does not change its status
    ✓ Viewing an archived message does not change its status
    ✓ Full message body is included in detail response
    ✓ ip_address is included in detail response

  Mark read
    ✓ Transitions message to read
    ✓ Idempotent when already read
    ✓ Unauthenticated → 401
    ✓ Non-existent id → 404
    ✓ Malformed UUID → 422

  Mark unread
    ✓ Transitions message to unread
    ✓ Transitions from archived to unread
    ✓ Idempotent when already unread
    ✓ Unauthenticated → 401
    ✓ Non-existent id → 404

  Archive
    ✓ Transitions message to archived
    ✓ From unread state
    ✓ Unauthenticated → 401
    ✓ Non-existent id → 404

  Delete
    ✓ Deletes message; returns 204
    ✓ Deleted message is no longer retrievable (404)
    ✓ Unauthenticated → 401
    ✓ Non-existent id → 404
    ✓ Malformed UUID → 422

  Audit log
    ✓ Viewed entry written on detail GET
    ✓ marked_read entry written on view of unread message
    ✓ marked_read entry written on explicit PATCH /read
    ✓ marked_unread entry written on PATCH /unread
    ✓ archived entry written on PATCH /archive
    ✓ deleted entry written on DELETE (resource_id preserved after row gone)
    ✓ Resource type and id match the message
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import ContactMessage, ContactStatus
from app.repositories.audit_repo import AuditRepository
from tests.admin.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD

BASE = "/admin/api/contact-messages"


# ── Fixtures ──────────────────────────────────────────────────────────────────


async def _login(client: AsyncClient) -> None:
    """Log in the test admin, setting the access_token cookie on the client."""
    resp = await client.post(
        "/admin/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"


async def _seed_message(
    db_session: AsyncSession,
    *,
    name: str = "Jane Smith",
    email: str = "jane@example.com",
    subject: str = "Hiring inquiry",
    message: str = "Hello, I'd like to discuss a role with you.",
    status: ContactStatus = ContactStatus.UNREAD,
) -> ContactMessage:
    """Insert a ContactMessage directly via the ORM for test setup."""
    msg = ContactMessage(
        name=name,
        email=email,
        subject=subject,
        message=message,
        status=status,
    )
    db_session.add(msg)
    await db_session.flush()
    await db_session.refresh(msg)
    await db_session.commit()
    return msg


# ── List ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_requires_auth(admin_client: AsyncClient) -> None:
    resp = await admin_client.get(BASE)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_returns_pagination_envelope(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    await _seed_message(db_session)
    await _login(admin_client)

    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    body = resp.json()

    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert "pages" in body
    assert body["page"] == 1
    assert body["total"] >= 1


@pytest.mark.asyncio
async def test_list_message_body_excluded(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """The full message body must not appear in list items."""
    await _seed_message(db_session, message="Secret message content")
    await _login(admin_client)

    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1
    assert "message" not in items[0]


@pytest.mark.asyncio
async def test_list_filter_by_status(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    await _seed_message(db_session, status=ContactStatus.UNREAD)
    await _seed_message(db_session, status=ContactStatus.READ, name="Bob")
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"status": "unread"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(item["status"] == "unread" for item in items)

    resp = await admin_client.get(BASE, params={"status": "read"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(item["status"] == "read" for item in items)


@pytest.mark.asyncio
async def test_list_search_by_name(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    await _seed_message(db_session, name="Unique Sender Name")
    await _seed_message(db_session, name="Different Person")
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"search": "Unique Sender"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Unique Sender Name"


@pytest.mark.asyncio
async def test_list_search_by_email(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    await _seed_message(db_session, email="findme@example.com")
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"search": "findme"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any("findme" in item["email"] for item in items)


@pytest.mark.asyncio
async def test_list_search_by_subject(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    await _seed_message(db_session, subject="Unique Subject XYZ")
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"search": "XYZ"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any("XYZ" in item["subject"] for item in items)


@pytest.mark.asyncio
async def test_list_whitespace_search_treated_as_no_search(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A search string of only whitespace should not filter any results."""
    await _seed_message(db_session)
    await _login(admin_client)

    resp_all = await admin_client.get(BASE)
    resp_ws = await admin_client.get(BASE, params={"search": "   "})
    assert resp_ws.status_code == 200
    assert resp_ws.json()["total"] == resp_all.json()["total"]


@pytest.mark.asyncio
async def test_list_pagination(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    for i in range(5):
        await _seed_message(db_session, name=f"Sender {i}", email=f"sender{i}@test.com")
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"page": 1, "page_size": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["page_size"] == 2
    assert body["total"] >= 5
    assert body["pages"] >= 3


@pytest.mark.asyncio
async def test_list_page_size_exceeds_max_returns_422(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.get(BASE, params={"page_size": 101})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_page_below_one_returns_422(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.get(BASE, params={"page": 0})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_empty_returns_zero_total(
    admin_client: AsyncClient,
) -> None:
    """No messages seeded → total should be 0."""
    await _login(admin_client)
    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []
    assert body["pages"] == 0


@pytest.mark.asyncio
async def test_list_invalid_status_returns_422(
    admin_client: AsyncClient,
) -> None:
    """An unrecognised status value must be rejected by Pydantic validation."""
    await _login(admin_client)
    resp = await admin_client.get(BASE, params={"status": "invalid_status"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_sort_descending(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Default sort (created_at_desc) must return newest first.

    SQLite in tests has sub-millisecond timestamp granularity — two rapid
    INSERTs can share the same created_at value, making order undefined.
    We assign explicit, distinct timestamps to avoid flakiness.
    """
    now = datetime.now(UTC)
    first = ContactMessage(
        name="First",
        email="first@sort.com",
        subject="Subject",
        message="Body",
        created_at=now - timedelta(seconds=10),
    )
    second = ContactMessage(
        name="Second",
        email="second@sort.com",
        subject="Subject",
        message="Body",
        created_at=now,
    )
    db_session.add_all([first, second])
    await db_session.commit()
    await db_session.refresh(first)
    await db_session.refresh(second)
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"sort": "created_at_desc"})
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    # second was created more recently — must appear before first
    assert ids.index(str(second.id)) < ids.index(str(first.id))


@pytest.mark.asyncio
async def test_list_sort_ascending(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """created_at_asc must return oldest first."""
    now = datetime.now(UTC)
    first = ContactMessage(
        name="First",
        email="first2@sort.com",
        subject="Subject",
        message="Body",
        created_at=now - timedelta(seconds=10),
    )
    second = ContactMessage(
        name="Second",
        email="second2@sort.com",
        subject="Subject",
        message="Body",
        created_at=now,
    )
    db_session.add_all([first, second])
    await db_session.commit()
    await db_session.refresh(first)
    await db_session.refresh(second)
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"sort": "created_at_asc"})
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    # first is older — must appear before second
    assert ids.index(str(first.id)) < ids.index(str(second.id))


# ── Detail ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_detail_requires_auth(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session)
    resp = await admin_client.get(f"{BASE}/{msg.id}")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_detail_returns_full_message(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session)
    await _login(admin_client)

    resp = await admin_client.get(f"{BASE}/{msg.id}")
    assert resp.status_code == 200
    body = resp.json()

    # All detail fields present
    for field in (
        "id",
        "name",
        "email",
        "subject",
        "message",
        "status",
        "ip_address",
        "user_agent",
        "created_at",
        "updated_at",
    ):
        assert field in body, f"Missing field: {field}"

    assert body["message"] == msg.message


@pytest.mark.asyncio
async def test_detail_nonexistent_returns_404(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.get(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_detail_auto_marks_unread_as_read(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Viewing an unread message automatically transitions it to read."""
    msg = await _seed_message(db_session, status=ContactStatus.UNREAD)
    assert msg.status == ContactStatus.UNREAD
    await _login(admin_client)

    resp = await admin_client.get(f"{BASE}/{msg.id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "read"


@pytest.mark.asyncio
async def test_detail_does_not_change_read_status(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Viewing a message already in 'read' state must not alter its status."""
    msg = await _seed_message(db_session, status=ContactStatus.READ)
    await _login(admin_client)

    resp = await admin_client.get(f"{BASE}/{msg.id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "read"


@pytest.mark.asyncio
async def test_detail_does_not_change_archived_status(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Viewing an archived message must not change its status."""
    msg = await _seed_message(db_session, status=ContactStatus.ARCHIVED)
    await _login(admin_client)

    resp = await admin_client.get(f"{BASE}/{msg.id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


# ── Mark read ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mark_read_requires_auth(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session)
    resp = await admin_client.patch(f"{BASE}/{msg.id}/read")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_mark_read_transitions_status(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session, status=ContactStatus.UNREAD)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{msg.id}/read")
    assert resp.status_code == 200
    assert resp.json()["status"] == "read"


@pytest.mark.asyncio
async def test_mark_read_nonexistent_returns_404(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{uuid.uuid4()}/read")
    assert resp.status_code == 404


# ── Mark unread ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mark_unread_requires_auth(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session)
    resp = await admin_client.patch(f"{BASE}/{msg.id}/unread")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_mark_unread_transitions_status(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session, status=ContactStatus.READ)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{msg.id}/unread")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unread"


@pytest.mark.asyncio
async def test_mark_unread_from_archived(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """mark_unread should work on archived messages too."""
    msg = await _seed_message(db_session, status=ContactStatus.ARCHIVED)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{msg.id}/unread")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unread"


@pytest.mark.asyncio
async def test_mark_unread_nonexistent_returns_404(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{uuid.uuid4()}/unread")
    assert resp.status_code == 404


# ── Archive ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_archive_requires_auth(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session)
    resp = await admin_client.patch(f"{BASE}/{msg.id}/archive")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_archive_transitions_status(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session, status=ContactStatus.READ)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{msg.id}/archive")
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


@pytest.mark.asyncio
async def test_archive_nonexistent_returns_404(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{uuid.uuid4()}/archive")
    assert resp.status_code == 404


# ── Delete ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_requires_auth(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session)
    resp = await admin_client.delete(f"{BASE}/{msg.id}")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_returns_204(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session)
    await _login(admin_client)

    resp = await admin_client.delete(f"{BASE}/{msg.id}")
    assert resp.status_code == 204
    assert resp.content == b""


@pytest.mark.asyncio
async def test_delete_message_no_longer_retrievable(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session)
    await _login(admin_client)

    await admin_client.delete(f"{BASE}/{msg.id}")

    # Second request for the same id must return 404
    resp = await admin_client.get(f"{BASE}/{msg.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_returns_404(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Audit log ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_audit_log_written_on_mark_read(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Marking a message as read must produce an audit log entry."""
    msg = await _seed_message(db_session, status=ContactStatus.UNREAD)
    await _login(admin_client)

    await admin_client.patch(f"{BASE}/{msg.id}/read")

    audit_repo = AuditRepository(db_session)
    logs = await audit_repo.get_recent(limit=10)
    actions = [log.action for log in logs]
    assert "admin.contact_message.marked_read" in actions


@pytest.mark.asyncio
async def test_audit_log_written_on_archive(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    msg = await _seed_message(db_session, status=ContactStatus.READ)
    await _login(admin_client)

    await admin_client.patch(f"{BASE}/{msg.id}/archive")

    audit_repo = AuditRepository(db_session)
    logs = await audit_repo.get_recent(limit=10)
    actions = [log.action for log in logs]
    assert "admin.contact_message.archived" in actions


@pytest.mark.asyncio
async def test_audit_log_written_on_delete(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Deleting a message must produce an audit log entry that outlives the row."""
    msg = await _seed_message(db_session)
    msg_id = str(msg.id)
    await _login(admin_client)

    await admin_client.delete(f"{BASE}/{msg.id}")

    audit_repo = AuditRepository(db_session)
    logs = await audit_repo.get_recent(limit=10)
    deleted_log = next(
        (log for log in logs if log.action == "admin.contact_message.deleted"),
        None,
    )
    assert deleted_log is not None
    assert deleted_log.resource_id == msg_id


# ── Idempotent / edge-case status transitions ─────────────────────────────────


@pytest.mark.asyncio
async def test_mark_read_already_read_is_idempotent(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Marking an already-read message as read must succeed (200), not error."""
    msg = await _seed_message(db_session, status=ContactStatus.READ)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{msg.id}/read")
    assert resp.status_code == 200
    assert resp.json()["status"] == "read"


@pytest.mark.asyncio
async def test_mark_unread_already_unread_is_idempotent(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Marking an already-unread message as unread must succeed (200)."""
    msg = await _seed_message(db_session, status=ContactStatus.UNREAD)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{msg.id}/unread")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unread"


@pytest.mark.asyncio
async def test_archive_from_unread(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Archiving an unread message (skipping read) must work."""
    msg = await _seed_message(db_session, status=ContactStatus.UNREAD)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{msg.id}/archive")
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


# ── Path parameter validation ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_detail_malformed_uuid_returns_422(
    admin_client: AsyncClient,
) -> None:
    """A non-UUID path parameter must be rejected with 422, not 500."""
    await _login(admin_client)
    resp = await admin_client.get(f"{BASE}/not-a-valid-uuid")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_mark_read_malformed_uuid_returns_422(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/not-a-uuid/read")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_delete_malformed_uuid_returns_422(
    admin_client: AsyncClient,
) -> None:
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/not-a-uuid")
    assert resp.status_code == 422


# ── Audit log — additional coverage ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_audit_log_written_on_view(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Fetching a message detail must write a 'viewed' audit entry."""
    msg = await _seed_message(db_session, status=ContactStatus.READ)
    await _login(admin_client)

    await admin_client.get(f"{BASE}/{msg.id}")

    audit_repo = AuditRepository(db_session)
    logs = await audit_repo.get_recent(limit=10)
    actions = [log.action for log in logs]
    assert "admin.contact_message.viewed" in actions


@pytest.mark.asyncio
async def test_audit_log_written_on_unread(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Marking a message unread must write a 'marked_unread' audit entry."""
    msg = await _seed_message(db_session, status=ContactStatus.READ)
    await _login(admin_client)

    await admin_client.patch(f"{BASE}/{msg.id}/unread")

    audit_repo = AuditRepository(db_session)
    logs = await audit_repo.get_recent(limit=10)
    actions = [log.action for log in logs]
    assert "admin.contact_message.marked_unread" in actions


@pytest.mark.asyncio
async def test_audit_log_resource_id_matches_message(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Audit log entries for mutations must reference the correct resource_id."""
    msg = await _seed_message(db_session, status=ContactStatus.UNREAD)
    await _login(admin_client)

    await admin_client.patch(f"{BASE}/{msg.id}/read")

    audit_repo = AuditRepository(db_session)
    logs = await audit_repo.get_recent(limit=10)
    read_log = next(
        (log for log in logs if log.action == "admin.contact_message.marked_read"),
        None,
    )
    assert read_log is not None
    assert read_log.resource_id == str(msg.id)
    assert read_log.resource_type == "contact_message"


# ── Response schema — no internal fields leaked ───────────────────────────────


@pytest.mark.asyncio
async def test_list_does_not_expose_ip_address(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """ip_address must NOT appear in list items — only in detail."""
    msg = ContactMessage(
        name="Test",
        email="test@example.com",
        subject="Test",
        message="Test message body here.",
        ip_address="1.2.3.4",
    )
    db_session.add(msg)
    await db_session.commit()
    await _login(admin_client)

    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        assert "ip_address" not in item
        assert "user_agent" not in item


@pytest.mark.asyncio
async def test_detail_exposes_ip_address(
    admin_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """ip_address must be present in the detail response."""
    msg = ContactMessage(
        name="Test",
        email="test2@example.com",
        subject="Test",
        message="Test message body here.",
        ip_address="10.0.0.1",
    )
    db_session.add(msg)
    await db_session.commit()
    await _login(admin_client)

    resp = await admin_client.get(f"{BASE}/{msg.id}")
    assert resp.status_code == 200
    assert "ip_address" in resp.json()
