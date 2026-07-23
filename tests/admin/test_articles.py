"""Tests for admin article endpoints — /admin/api/articles."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleStatus
from app.repositories.audit_repo import AuditRepository
from tests.admin.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD

BASE = "/admin/api/articles"


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
    slug: str = "seed-article",
    title: str = "Seed Article",
    status: ArticleStatus = ArticleStatus.DRAFT,
    featured: bool = False,
    category: str = "Backend",
) -> Article:
    article = Article(
        slug=slug,
        title=title,
        summary="A summary.",
        body="# Body\n\nContent.",
        category=category,
        status=status,
        tags=["python"],
        featured=featured,
        published_at=datetime.now(UTC) if status == ArticleStatus.PUBLISHED else None,
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


_VALID_CREATE = {
    "title": "How to Build a FastAPI Backend",
    "summary": "A practical guide to layered architecture in FastAPI.",
    "body": "# Introduction\n\nThis is the full article content.",
    "category": "FastAPI",
    "tags": ["fastapi", "python", "backend"],
    "featured": False,
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


# ── List ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_returns_all_statuses(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="d1", status=ArticleStatus.DRAFT)
    await _seed(db_session, slug="p1", status=ArticleStatus.PUBLISHED)
    await _seed(db_session, slug="a1", status=ArticleStatus.ARCHIVED)
    await _login(admin_client)

    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


@pytest.mark.asyncio
async def test_list_filter_by_status(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="d2", status=ArticleStatus.DRAFT)
    await _seed(db_session, slug="p2", status=ArticleStatus.PUBLISHED)
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"status": "draft"})
    body = resp.json()
    assert all(item["status"] == "draft" for item in body["items"])


@pytest.mark.asyncio
async def test_list_search_by_title(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="unique-xyz", title="Unique XYZ Title")
    await _seed(db_session, slug="other", title="Different Article")
    await _login(admin_client)

    resp = await admin_client.get(BASE, params={"search": "XYZ"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "unique-xyz"


@pytest.mark.asyncio
async def test_list_items_exclude_body(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="no-body-list")
    await _login(admin_client)
    resp = await admin_client.get(BASE)
    assert "body" not in resp.json()["items"][0]


# ── Create ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_returns_201(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.post(BASE, json=_VALID_CREATE)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_create_auto_generates_slug(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.post(BASE, json=_VALID_CREATE)
    body = resp.json()
    assert body["slug"] == "how-to-build-a-fastapi-backend"


@pytest.mark.asyncio
async def test_create_slug_uniqueness_collision(admin_client: AsyncClient) -> None:
    """Duplicate title → slug gets -2 suffix."""
    await _login(admin_client)
    await admin_client.post(BASE, json=_VALID_CREATE)
    resp2 = await admin_client.post(BASE, json=_VALID_CREATE)
    assert resp2.status_code == 201
    assert resp2.json()["slug"] == "how-to-build-a-fastapi-backend-2"


@pytest.mark.asyncio
async def test_create_initial_status_is_draft(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.post(BASE, json=_VALID_CREATE)
    assert resp.json()["status"] == "draft"


@pytest.mark.asyncio
async def test_create_calculates_reading_time(admin_client: AsyncClient) -> None:
    payload = {**_VALID_CREATE, "body": " ".join(["word"] * 400)}  # 400 words = 2 min
    await _login(admin_client)
    resp = await admin_client.post(BASE, json=payload)
    assert resp.json()["reading_time_minutes"] == 2


@pytest.mark.asyncio
async def test_create_missing_title_returns_422(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.post(BASE, json={**_VALID_CREATE, "title": ""})
    assert resp.status_code == 422


# ── Get detail ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_detail_includes_body(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="detail-test")
    await _login(admin_client)
    resp = await admin_client.get(f"{BASE}/{article.id}")
    assert resp.status_code == 200
    assert "body" in resp.json()


@pytest.mark.asyncio
async def test_get_detail_nonexistent_returns_404(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.get(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_title(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="to-update")
    await _login(admin_client)
    resp = await admin_client.put(f"{BASE}/{article.id}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_recalculates_reading_time(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="reading-time-update")
    await _login(admin_client)
    new_body = " ".join(["word"] * 600)  # 600 words = 3 min
    resp = await admin_client.put(f"{BASE}/{article.id}", json={"body": new_body})
    assert resp.json()["reading_time_minutes"] == 3


@pytest.mark.asyncio
async def test_update_nonexistent_returns_404(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.put(f"{BASE}/{uuid.uuid4()}", json={"title": "X"})
    assert resp.status_code == 404


# ── Publish ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_transitions_to_published(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="to-publish")
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{article.id}/publish")
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"


@pytest.mark.asyncio
async def test_publish_sets_published_at(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="publish-date")
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{article.id}/publish")
    assert resp.json()["published_at"] is not None


@pytest.mark.asyncio
async def test_publish_missing_body_returns_422(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Article with no body cannot be published."""
    article = Article(
        slug="no-body-pub",
        title="Title",
        summary="Summary",
        body=None,
        category="Backend",
        status=ArticleStatus.DRAFT,
        tags=[],
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{article.id}/publish")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_publish_nonexistent_returns_404(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{uuid.uuid4()}/publish")
    assert resp.status_code == 404


# ── Unpublish ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_unpublish_returns_draft_status(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="to-unpublish", status=ArticleStatus.PUBLISHED)
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{article.id}/unpublish")
    assert resp.status_code == 200
    assert resp.json()["status"] == "draft"


@pytest.mark.asyncio
async def test_unpublish_nonexistent_returns_404(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{uuid.uuid4()}/unpublish")
    assert resp.status_code == 404


# ── Archive ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_archive_transitions_status(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="to-archive")
    await _login(admin_client)
    resp = await admin_client.patch(f"{BASE}/{article.id}/archive")
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"


# ── Delete ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_returns_204(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="to-delete")
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/{article.id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_deleted_article_not_retrievable(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="gone-soon")
    article_id = article.id
    await _login(admin_client)
    await admin_client.delete(f"{BASE}/{article_id}")
    resp = await admin_client.get(f"{BASE}/{article_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_returns_404(admin_client: AsyncClient) -> None:
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Audit log ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_audit_log_on_create(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    await _login(admin_client)
    await admin_client.post(BASE, json=_VALID_CREATE)
    logs = await AuditRepository(db_session).get_recent(limit=5)
    assert any(log.action == "admin.article.created" for log in logs)


@pytest.mark.asyncio
async def test_audit_log_on_publish(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="audit-publish")
    await _login(admin_client)
    await admin_client.patch(f"{BASE}/{article.id}/publish")
    logs = await AuditRepository(db_session).get_recent(limit=5)
    assert any(log.action == "admin.article.published" for log in logs)


@pytest.mark.asyncio
async def test_audit_log_on_delete_persists_after_deletion(
    admin_client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="audit-delete")
    article_id = str(article.id)
    await _login(admin_client)
    await admin_client.delete(f"{BASE}/{article.id}")
    logs = await AuditRepository(db_session).get_recent(limit=5)
    deleted_log = next(
        (log for log in logs if log.action == "admin.article.deleted"), None
    )
    assert deleted_log is not None
    assert deleted_log.resource_id == article_id


# ── Publish→public visibility ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_published_article_visible_on_public_endpoint(
    admin_client: AsyncClient, client: AsyncClient, db_session: AsyncSession
) -> None:
    """Publishing an article makes it visible on the public list immediately."""
    article = await _seed(db_session, slug="soon-public")
    await _login(admin_client)

    # Before publish: not on public endpoint
    before = await client.get("/api/v1/articles")
    assert before.json()["total"] == 0

    # Publish
    await admin_client.patch(f"{BASE}/{article.id}/publish")

    # After publish: appears on public endpoint
    after = await client.get("/api/v1/articles")
    assert after.json()["total"] == 1
    assert after.json()["items"][0]["slug"] == "soon-public"


@pytest.mark.asyncio
async def test_unpublished_article_disappears_from_public(
    admin_client: AsyncClient, client: AsyncClient, db_session: AsyncSession
) -> None:
    article = await _seed(db_session, slug="going-private", status=ArticleStatus.PUBLISHED)
    await _login(admin_client)

    before = await client.get("/api/v1/articles")
    assert before.json()["total"] == 1

    await admin_client.patch(f"{BASE}/{article.id}/unpublish")

    after = await client.get("/api/v1/articles")
    assert after.json()["total"] == 0
