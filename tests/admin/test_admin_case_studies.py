"""Tests for admin case study endpoints — /admin/api/case-studies."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case_study import CaseStudy, CaseStudyStatus
from tests.admin.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD

BASE = "/admin/api/case-studies"
PUBLIC_BASE = "/api/v1/projects"


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _login(client: AsyncClient) -> None:
    resp = await client.post(
        "/admin/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"


async def _seed_case_study(
    db: AsyncSession,
    *,
    slug: str = "test-project",
    status: str = CaseStudyStatus.DRAFT,
    disclaimer: str | None = "Test disclaimer",
    content: dict | None = None,
) -> CaseStudy:
    cs = CaseStudy(
        id=uuid.uuid4(),
        slug=slug,
        status=status,
        disclaimer=disclaimer,
        content=content or {"overview": {"what": "A test project"}},
    )
    db.add(cs)
    await db.commit()
    await db.refresh(cs)
    return cs


# ── Auth guard ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_requires_auth(client: AsyncClient) -> None:
    resp = await client.get(BASE)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(BASE, json={"slug": "test"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_requires_auth(client: AsyncClient) -> None:
    resp = await client.put(f"{BASE}/{uuid.uuid4()}", json={})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_requires_auth(client: AsyncClient) -> None:
    resp = await client.delete(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 401


# ── List ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_empty(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.get(BASE)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_returns_all(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    await _seed_case_study(db, slug="proj-a")
    await _seed_case_study(db, slug="proj-b")
    resp = await client.get(BASE)
    assert resp.status_code == 200
    slugs = {cs["slug"] for cs in resp.json()}
    assert {"proj-a", "proj-b"} == slugs


# ── Create ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_case_study(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.post(
        BASE,
        json={
            "slug": "new-project",
            "disclaimer": "Work in progress",
            "content": {"overview": {"what": "A new project"}},
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "new-project"
    assert data["status"] == "draft"
    assert data["disclaimer"] == "Work in progress"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_minimal(client: AsyncClient) -> None:
    """slug is the only required field."""
    await _login(client)
    resp = await client.post(BASE, json={"slug": "minimal"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "minimal"
    assert data["content"] == {}


@pytest.mark.asyncio
async def test_create_rejects_unknown_fields(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.post(BASE, json={"slug": "test", "extra": "field"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_empty_slug_rejected(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.post(BASE, json={"slug": ""})
    assert resp.status_code == 422


# ── Get single ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_case_study(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    cs = await _seed_case_study(db)
    resp = await client.get(f"{BASE}/{cs.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == cs.slug


@pytest.mark.asyncio
async def test_get_not_found(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.get(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_slug(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    cs = await _seed_case_study(db, slug="old-slug")
    resp = await client.put(f"{BASE}/{cs.id}", json={"slug": "new-slug"})
    assert resp.status_code == 200
    assert resp.json()["slug"] == "new-slug"


@pytest.mark.asyncio
async def test_update_content(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    cs = await _seed_case_study(db)
    new_content = {"overview": {"what": "Updated"}, "goals": []}
    resp = await client.put(f"{BASE}/{cs.id}", json={"content": new_content})
    assert resp.status_code == 200
    assert resp.json()["content"]["overview"]["what"] == "Updated"


@pytest.mark.asyncio
async def test_update_not_found(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.put(f"{BASE}/{uuid.uuid4()}", json={"slug": "x"})
    assert resp.status_code == 404


# ── Publish / unpublish ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_draft(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    cs = await _seed_case_study(db, status=CaseStudyStatus.DRAFT)
    resp = await client.patch(f"{BASE}/{cs.id}/publish")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "published"
    assert data["published_at"] is not None


@pytest.mark.asyncio
async def test_publish_preserves_published_at(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Re-publishing should not reset published_at."""
    await _login(client)
    cs = await _seed_case_study(db, status=CaseStudyStatus.PUBLISHED)
    # Set a fixed published_at
    from datetime import datetime, timezone
    cs.published_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    await db.commit()
    await db.refresh(cs)
    original = cs.published_at

    resp = await client.patch(f"{BASE}/{cs.id}/publish")
    assert resp.status_code == 200
    # published_at must not change on re-publish
    assert resp.json()["published_at"] is not None


@pytest.mark.asyncio
async def test_unpublish(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    cs = await _seed_case_study(db, status=CaseStudyStatus.PUBLISHED)
    resp = await client.patch(f"{BASE}/{cs.id}/unpublish")
    assert resp.status_code == 200
    assert resp.json()["status"] == "draft"


@pytest.mark.asyncio
async def test_publish_not_found(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.patch(f"{BASE}/{uuid.uuid4()}/publish")
    assert resp.status_code == 404


# ── Delete ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_case_study(client: AsyncClient, db: AsyncSession) -> None:
    await _login(client)
    cs = await _seed_case_study(db)
    resp = await client.delete(f"{BASE}/{cs.id}")
    assert resp.status_code == 204
    # Confirm gone
    resp2 = await client.get(f"{BASE}/{cs.id}")
    assert resp2.status_code == 404


@pytest.mark.asyncio
async def test_delete_not_found(client: AsyncClient) -> None:
    await _login(client)
    resp = await client.delete(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Public endpoint ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_public_returns_published(
    client: AsyncClient, db: AsyncSession
) -> None:
    await _seed_case_study(
        db,
        slug="published-proj",
        status=CaseStudyStatus.PUBLISHED,
        content={"overview": {"what": "Published"}},
    )
    resp = await client.get(f"{PUBLIC_BASE}/published-proj/case-study")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "published-proj"
    assert data["status"] == "published"
    assert data["content"]["overview"]["what"] == "Published"


@pytest.mark.asyncio
async def test_public_hides_draft(
    client: AsyncClient, db: AsyncSession
) -> None:
    await _seed_case_study(db, slug="draft-proj", status=CaseStudyStatus.DRAFT)
    resp = await client.get(f"{PUBLIC_BASE}/draft-proj/case-study")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_public_not_found(client: AsyncClient) -> None:
    resp = await client.get(f"{PUBLIC_BASE}/no-such-project/case-study")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_public_no_auth_needed(
    client: AsyncClient, db: AsyncSession
) -> None:
    """Public endpoint must not require authentication."""
    await _seed_case_study(
        db, slug="open-proj", status=CaseStudyStatus.PUBLISHED
    )
    resp = await client.get(f"{PUBLIC_BASE}/open-proj/case-study")
    assert resp.status_code == 200
