"""Tests for admin project endpoints — /admin/api/projects."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.models.audit_log import AdminAuditLog
from app.models.project import Project, ProjectStatus
from tests.admin.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD

BASE = "/admin/api/projects"


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _login(client: AsyncClient) -> None:
    resp = await client.post(
        "/admin/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"


async def _seed(
    db: AsyncSession,
    *,
    slug: str = "seed-project",
    title: str = "Seed Project",
    status: ProjectStatus = ProjectStatus.DRAFT,
    featured: bool = False,
    category: str = "Backend",
    display_order: int = 0,
) -> Project:
    project = Project(
        slug=slug,
        title=title,
        subtitle="A subtitle",
        description="A detailed description of the project.",
        category=category,
        status=status,
        tech_stack=["Python"],
        is_featured=featured,
        display_order=display_order,
        links=[],
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


_VALID_CREATE = {
    "title": "My Async API Project",
    "description": "A FastAPI project with async support.",
    "category": "Backend",
    "tech_stack": ["Python", "FastAPI"],
    "is_featured": False,
    "display_order": 0,
    "links": [],
}


# ── Auth ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_requires_auth(admin_client: AsyncClient) -> None:
    resp = await admin_client.get(BASE)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_requires_auth(admin_client: AsyncClient) -> None:
    resp = await admin_client.post(BASE, json=_VALID_CREATE)
    assert resp.status_code == 401


# ── Create ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_returns_201(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.post(BASE, json=_VALID_CREATE)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "draft"
    assert body["slug"] == "my-async-api-project"
    assert body["title"] == _VALID_CREATE["title"]


@pytest.mark.asyncio
async def test_create_generates_unique_slug(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session, slug="my-async-api-project")
    await _login(admin_client)
    resp = await admin_client.post(BASE, json=_VALID_CREATE)
    assert resp.status_code == 201
    assert resp.json()["slug"] == "my-async-api-project-2"


@pytest.mark.asyncio
async def test_create_validates_missing_title(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    payload = {**_VALID_CREATE, "title": ""}
    resp = await admin_client.post(BASE, json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_validates_thumbnail_url_must_be_http(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    payload = {**_VALID_CREATE, "thumbnail_url": "javascript:alert(1)"}
    resp = await admin_client.post(BASE, json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_accepts_valid_thumbnail_url(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    payload = {**_VALID_CREATE, "thumbnail_url": "https://cdn.example.com/img.png"}
    resp = await admin_client.post(BASE, json=payload)
    assert resp.status_code == 201
    assert resp.json()["thumbnail_url"] == "https://cdn.example.com/img.png"


@pytest.mark.asyncio
async def test_create_validates_link_href_must_be_http(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    payload = {
        **_VALID_CREATE,
        "links": [{"label": "Repo", "href": "javascript:void(0)", "type": "github"}],
    }
    resp = await admin_client.post(BASE, json=payload)
    assert resp.status_code == 422


# ── List ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_returns_all_statuses(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session, slug="d1", status=ProjectStatus.DRAFT)
    await _seed(db_session, slug="p1", status=ProjectStatus.PUBLISHED)
    await _seed(db_session, slug="a1", status=ProjectStatus.ARCHIVED)
    await _login(admin_client)

    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


@pytest.mark.asyncio
async def test_list_filter_by_status(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session, slug="d1", status=ProjectStatus.DRAFT)
    await _seed(db_session, slug="p1", status=ProjectStatus.PUBLISHED)
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"status": "draft"})
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["slug"] == "d1"


@pytest.mark.asyncio
async def test_list_search(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed(db_session, slug="fastapi-proj", title="FastAPI Project")
    await _seed(db_session, slug="django-proj",  title="Django Project")
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"search": "fastapi"})
    assert resp.json()["total"] == 1


# ── Detail ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session)
    await _login(admin_client)

    resp = await admin_client.get(f"{BASE}/{project.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(project.id)


@pytest.mark.asyncio
async def test_get_not_found_returns_404(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.get(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session)
    await _login(admin_client)

    resp = await admin_client.put(f"{BASE}/{project.id}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_not_found_returns_404(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.put(f"{BASE}/{uuid.uuid4()}", json={"title": "X"})
    assert resp.status_code == 404


# ── Status transitions ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{project.id}/publish")
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"


@pytest.mark.asyncio
async def test_publish_not_found_returns_404(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{uuid.uuid4()}/publish")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unpublish_returns_draft(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session, status=ProjectStatus.PUBLISHED)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{project.id}/unpublish")
    assert resp.status_code == 200
    assert resp.json()["status"] == "draft"


@pytest.mark.asyncio
async def test_archive_returns_archived(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session, status=ProjectStatus.PUBLISHED)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{project.id}/archive")
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


# ── Feature toggle ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_feature_toggle_sets_true(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session, featured=False)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{project.id}/feature")
    assert resp.status_code == 200
    assert resp.json()["is_featured"] is True


@pytest.mark.asyncio
async def test_feature_toggle_sets_false(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session, featured=True)
    await _login(admin_client)

    resp = await admin_client.patch(f"{BASE}/{project.id}/feature")
    assert resp.status_code == 200
    assert resp.json()["is_featured"] is False


@pytest.mark.asyncio
async def test_multiple_projects_can_be_featured(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    p1 = await _seed(db_session, slug="p1", featured=False)
    p2 = await _seed(db_session, slug="p2", featured=False)
    await _login(admin_client)

    await admin_client.patch(f"{BASE}/{p1.id}/feature")
    await admin_client.patch(f"{BASE}/{p2.id}/feature")

    resp1 = await admin_client.get(f"{BASE}/{p1.id}")
    resp2 = await admin_client.get(f"{BASE}/{p2.id}")
    assert resp1.json()["is_featured"] is True
    assert resp2.json()["is_featured"] is True


# ── Reorder ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reorder_returns_204(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    p1 = await _seed(db_session, slug="r1", display_order=0)
    p2 = await _seed(db_session, slug="r2", display_order=1)
    await _login(admin_client)

    payload = {
        "items": [
            {"id": str(p1.id), "display_order": 10},
            {"id": str(p2.id), "display_order": 5},
        ]
    }
    resp = await admin_client.patch(f"{BASE}/reorder", json=payload)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_reorder_unknown_id_returns_422(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    payload = {"items": [{"id": str(uuid.uuid4()), "display_order": 1}]}
    resp = await admin_client.patch(f"{BASE}/reorder", json=payload)
    assert resp.status_code == 422


# ── Delete ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_returns_204(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session)
    await _login(admin_client)

    resp = await admin_client.delete(f"{BASE}/{project.id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_not_found_returns_404(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Audit logging ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_audit_log_written_on_create(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.post(BASE, json=_VALID_CREATE)
    assert resp.status_code == 201

    result = await db_session.execute(
        select(AdminAuditLog).where(AdminAuditLog.action == "admin.project.created")
    )
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_audit_log_written_on_delete(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    project = await _seed(db_session)
    await _login(admin_client)
    await admin_client.delete(f"{BASE}/{project.id}")

    result = await db_session.execute(
        select(AdminAuditLog).where(AdminAuditLog.action == "admin.project.deleted")
    )
    assert result.scalar_one_or_none() is not None
