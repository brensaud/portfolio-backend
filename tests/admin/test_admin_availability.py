"""Tests for admin availability endpoints — /admin/api/availability."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AdminAuditLog
from app.models.availability import Availability
from tests.admin.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD

BASE = "/admin/api/availability"


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _login(client: AsyncClient) -> None:
    resp = await client.post(
        "/admin/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"


async def _seed(db: AsyncSession) -> Availability:
    row = Availability(id=1, status="available")
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


# ── Auth ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_requires_auth(admin_client: AsyncClient) -> None:
    resp = await admin_client.get(BASE)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_requires_auth(admin_client: AsyncClient) -> None:
    resp = await admin_client.put(BASE, json={"status": "available"})
    assert resp.status_code == 401


# ── Get ───────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session)
    await _login(admin_client)

    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "available"
    assert "updated_at" in body
    assert "id" in body


@pytest.mark.asyncio
async def test_get_creates_default_row_if_missing(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    """Service must upsert if the singleton row doesn't exist."""
    await _login(admin_client)
    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    assert resp.json()["status"] == "available"


# ── Update ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session)
    await _login(admin_client)

    payload = {
        "status": "limited",
        "message": "Available for select roles only.",
        "notice_period_weeks": 4,
    }
    resp = await admin_client.put(BASE, json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "limited"
    assert body["message"] == "Available for select roles only."
    assert body["notice_period_weeks"] == 4


@pytest.mark.asyncio
async def test_update_validates_status_enum(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session)
    await _login(admin_client)

    resp = await admin_client.put(BASE, json={"status": "open"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_all_valid_statuses(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session)
    await _login(admin_client)

    for s in ("available", "limited", "unavailable"):
        resp = await admin_client.put(BASE, json={"status": s})
        assert resp.status_code == 200
        assert resp.json()["status"] == s


@pytest.mark.asyncio
async def test_update_notice_period_weeks_bounds(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session)
    await _login(admin_client)

    # Below minimum
    resp = await admin_client.put(BASE, json={"status": "available", "notice_period_weeks": 0})
    assert resp.status_code == 422

    # Above maximum
    resp = await admin_client.put(BASE, json={"status": "available", "notice_period_weeks": 53})
    assert resp.status_code == 422


# ── Audit ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_audit_log_written_on_update(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session)
    await _login(admin_client)

    await admin_client.put(BASE, json={"status": "unavailable"})

    result = await db_session.execute(
        select(AdminAuditLog).where(AdminAuditLog.action == "admin.availability.updated")
    )
    assert result.scalar_one_or_none() is not None
