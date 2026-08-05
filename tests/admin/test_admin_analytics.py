"""Tests for analytics endpoints — public POST and admin GET."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.page_view import PageView
from tests.admin.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD

PUBLIC_URL = "/api/v1/analytics/view"
ADMIN_BASE  = "/admin/api/analytics"


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _login(client: AsyncClient) -> None:
    resp = await client.post(
        "/admin/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"


async def _seed_views(db: AsyncSession, *, count: int = 3) -> None:
    import uuid
    for i in range(count):
        pv = PageView(
            id=uuid.uuid4(),
            path=f"/work/project-{i}",
            session_id=f"session-{i:04d}",
            referrer="https://google.com" if i % 2 == 0 else None,
            country="US" if i % 3 == 0 else None,
        )
        db.add(pv)
    await db.commit()


# ── Public: record view ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_record_view_no_auth(client: AsyncClient) -> None:
    """Public endpoint — no authentication required."""
    resp = await client.post(
        PUBLIC_URL,
        json={"path": "/work/test-project", "session_id": "abc123"},
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_record_view_with_referrer(client: AsyncClient) -> None:
    resp = await client.post(
        PUBLIC_URL,
        json={
            "path": "/writing/my-article",
            "session_id": "sess-ref-test",
            "referrer": "https://linkedin.com",
        },
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_record_view_empty_path_rejected(client: AsyncClient) -> None:
    resp = await client.post(PUBLIC_URL, json={"path": "", "session_id": "s1"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_record_view_missing_session_rejected(client: AsyncClient) -> None:
    resp = await client.post(PUBLIC_URL, json={"path": "/work/x"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_record_view_deduplication(client: AsyncClient, db: AsyncSession) -> None:
    """Same session + path within 30 min should not create a second row."""
    body = {"path": "/work/dedup-test", "session_id": "dedup-session-1"}
    r1 = await client.post(PUBLIC_URL, json=body)
    r2 = await client.post(PUBLIC_URL, json=body)
    assert r1.status_code == 204
    assert r2.status_code == 204
    result = await db.execute(
        __import__("sqlalchemy", fromlist=["select"]).select(PageView).where(
            PageView.session_id == "dedup-session-1",
            PageView.path == "/work/dedup-test",
        )
    )
    rows = result.scalars().all()
    assert len(rows) == 1  # deduplicated


@pytest.mark.asyncio
async def test_record_view_different_paths_both_recorded(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Same session, different paths → both recorded."""
    session = "multi-path-session"
    await client.post(PUBLIC_URL, json={"path": "/work/a", "session_id": session})
    await client.post(PUBLIC_URL, json={"path": "/work/b", "session_id": session})
    from sqlalchemy import select
    result = await db.execute(
        select(PageView).where(PageView.session_id == session)
    )
    assert len(result.scalars().all()) == 2


# ── Admin: auth guard ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_summary_requires_auth(client: AsyncClient) -> None:
    resp = await client.get(f"{ADMIN_BASE}/summary")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_pages_requires_auth(client: AsyncClient) -> None:
    resp = await client.get(f"{ADMIN_BASE}/pages")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_referrers_requires_auth(client: AsyncClient) -> None:
    resp = await client.get(f"{ADMIN_BASE}/referrers")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_countries_requires_auth(client: AsyncClient) -> None:
    resp = await client.get(f"{ADMIN_BASE}/countries")
    assert resp.status_code == 401


# ── Admin: summary ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_summary_empty(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.get(f"{ADMIN_BASE}/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_views"] == 0
    assert data["unique_sessions"] == 0
    assert data["top_page"] is None
    assert data["daily"] == []


@pytest.mark.asyncio
async def test_summary_with_data(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    await _seed_views(db, count=5)
    resp = await client.get(f"{ADMIN_BASE}/summary?period=all")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_views"] == 5
    assert data["unique_sessions"] == 5
    assert data["top_page"] is not None
    assert isinstance(data["daily"], list)


@pytest.mark.asyncio
async def test_summary_period_7d(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    await _seed_views(db, count=3)
    resp = await client.get(f"{ADMIN_BASE}/summary?period=7d")
    assert resp.status_code == 200
    assert resp.json()["period"] == "7d"


@pytest.mark.asyncio
async def test_summary_invalid_period_falls_back(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.get(f"{ADMIN_BASE}/summary?period=invalid")
    assert resp.status_code == 200
    assert resp.json()["period"] == "7d"  # fallback


# ── Admin: pages ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pages_empty(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.get(f"{ADMIN_BASE}/pages")
    assert resp.status_code == 200
    assert resp.json()["pages"] == []


@pytest.mark.asyncio
async def test_pages_with_data(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    await _seed_views(db, count=4)
    resp = await client.get(f"{ADMIN_BASE}/pages?period=all&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["pages"]) > 0
    assert "path" in data["pages"][0]
    assert "views" in data["pages"][0]


# ── Admin: referrers ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_referrers_empty(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.get(f"{ADMIN_BASE}/referrers")
    assert resp.status_code == 200
    assert resp.json()["referrers"] == []


@pytest.mark.asyncio
async def test_referrers_with_data(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    await _seed_views(db, count=4)  # seeds 2 with referrer=https://google.com
    resp = await client.get(f"{ADMIN_BASE}/referrers?period=all")
    assert resp.status_code == 200
    referrers = resp.json()["referrers"]
    assert len(referrers) > 0
    assert referrers[0]["referrer"] == "https://google.com"


# ── Admin: countries ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_countries_empty(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.get(f"{ADMIN_BASE}/countries")
    assert resp.status_code == 200
    assert resp.json()["countries"] == []


@pytest.mark.asyncio
async def test_countries_with_data(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    await _seed_views(db, count=6)  # seeds 2 with country=US
    resp = await client.get(f"{ADMIN_BASE}/countries?period=all")
    assert resp.status_code == 200
    countries = resp.json()["countries"]
    assert len(countries) > 0
    assert countries[0]["country"] == "US"
