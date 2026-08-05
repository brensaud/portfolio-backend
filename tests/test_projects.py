"""Tests for GET /api/v1/projects and GET /api/v1/projects/{slug}."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus

PUBLIC_LIST   = "/api/v1/projects"
PUBLIC_DETAIL = "/api/v1/projects/{slug}"


# ── Seed helper ───────────────────────────────────────────────────────────────


async def _seed(
    db: AsyncSession,
    *,
    slug: str = "test-project",
    title: str = "Test Project",
    status: ProjectStatus = ProjectStatus.PUBLISHED,
    featured: bool = False,
    category: str = "Backend",
    display_order: int = 0,
) -> Project:
    project = Project(
        slug=slug,
        title=title,
        subtitle="A subtitle",
        description="A description of the project.",
        category=category,
        status=status,
        tech_stack=["Python", "FastAPI"],
        is_featured=featured,
        display_order=display_order,
        links=[],
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


# ── Public list ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_returns_200(client: AsyncClient) -> None:
    resp = await client.get(PUBLIC_LIST)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_empty_when_no_projects(client: AsyncClient) -> None:
    resp = await client.get(PUBLIC_LIST)
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []


@pytest.mark.asyncio
async def test_list_returns_only_published(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="pub", status=ProjectStatus.PUBLISHED)
    await _seed(db_session, slug="dra", status=ProjectStatus.DRAFT)
    await _seed(db_session, slug="arc", status=ProjectStatus.ARCHIVED)

    resp = await client.get(PUBLIC_LIST)
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "pub"


@pytest.mark.asyncio
async def test_list_ordered_by_display_order(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="b", display_order=10, status=ProjectStatus.PUBLISHED)
    await _seed(db_session, slug="a", display_order=1,  status=ProjectStatus.PUBLISHED)
    await _seed(db_session, slug="c", display_order=20, status=ProjectStatus.PUBLISHED)

    resp = await client.get(PUBLIC_LIST)
    slugs = [p["slug"] for p in resp.json()["items"]]
    assert slugs == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_list_filter_by_category(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="be", category="Backend", status=ProjectStatus.PUBLISHED)
    await _seed(db_session, slug="ai", category="AI",      status=ProjectStatus.PUBLISHED)

    resp = await client.get(PUBLIC_LIST, params={"category": "AI"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "ai"


@pytest.mark.asyncio
async def test_list_filter_by_featured(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="f1", featured=True,  status=ProjectStatus.PUBLISHED)
    await _seed(db_session, slug="f2", featured=False, status=ProjectStatus.PUBLISHED)

    resp = await client.get(PUBLIC_LIST, params={"featured": "true"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "f1"


@pytest.mark.asyncio
async def test_list_pagination(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    for i in range(5):
        await _seed(
            db_session,
            slug=f"proj-{i}",
            display_order=i,
            status=ProjectStatus.PUBLISHED,
        )

    resp = await client.get(PUBLIC_LIST, params={"page": 1, "page_size": 2})
    body = resp.json()
    assert body["total"] == 5
    assert body["pages"] == 3
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_list_response_shape(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session)
    body = resp.json() if (resp := await client.get(PUBLIC_LIST)) else None
    assert resp.status_code == 200
    item = body["items"][0]
    assert "id" in item
    assert "slug" in item
    assert "tech_stack" in item
    assert "is_featured" in item
    assert "display_order" in item
    assert "links" in item


# ── Public detail ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_by_slug_returns_200(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="my-project")
    resp = await client.get(PUBLIC_DETAIL.format(slug="my-project"))
    assert resp.status_code == 200
    assert resp.json()["slug"] == "my-project"


@pytest.mark.asyncio
async def test_get_by_slug_not_found_returns_404(client: AsyncClient) -> None:
    resp = await client.get(PUBLIC_DETAIL.format(slug="missing"))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_draft_returns_404(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="draft-proj", status=ProjectStatus.DRAFT)
    resp = await client.get(PUBLIC_DETAIL.format(slug="draft-proj"))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_archived_returns_404(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="arc-proj", status=ProjectStatus.ARCHIVED)
    resp = await client.get(PUBLIC_DETAIL.format(slug="arc-proj"))
    assert resp.status_code == 404
