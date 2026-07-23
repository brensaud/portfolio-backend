"""Tests for GET /api/v1/articles and GET /api/v1/articles/{slug}."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleStatus

PUBLIC_LIST = "/api/v1/articles"


# ── Seed helpers ─────────────────────────────────────────────────────────────


async def _seed(
    db: AsyncSession,
    *,
    slug: str = "test-article",
    title: str = "Test Article",
    status: ArticleStatus = ArticleStatus.PUBLISHED,
    featured: bool = False,
    category: str = "Backend",
    tags: list[str] | None = None,
) -> Article:
    article = Article(
        slug=slug,
        title=title,
        summary="A short summary.",
        body="# Heading\n\nSome content here.",
        category=category,
        status=status,
        tags=tags or ["python"],
        featured=featured,
        published_at=datetime.now(UTC) if status == ArticleStatus.PUBLISHED else None,
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


# ── Public list ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_returns_200(client: AsyncClient) -> None:
    resp = await client.get(PUBLIC_LIST)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_empty_when_no_articles(client: AsyncClient) -> None:
    resp = await client.get(PUBLIC_LIST)
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []
    assert body["pages"] == 0


@pytest.mark.asyncio
async def test_list_returns_published_only(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="pub", status=ArticleStatus.PUBLISHED)
    await _seed(db_session, slug="draft", status=ArticleStatus.DRAFT)
    await _seed(db_session, slug="archived", status=ArticleStatus.ARCHIVED)

    resp = await client.get(PUBLIC_LIST)
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "pub"


@pytest.mark.asyncio
async def test_list_pagination_envelope(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    for i in range(3):
        await _seed(db_session, slug=f"article-{i}", title=f"Article {i}")

    resp = await client.get(PUBLIC_LIST, params={"page": 1, "page_size": 2})
    body = resp.json()
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["pages"] == 2
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_list_page_size_max_50(client: AsyncClient) -> None:
    resp = await client.get(PUBLIC_LIST, params={"page_size": 51})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_filter_by_category(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="backend-1", category="Backend")
    await _seed(db_session, slug="fastapi-1", category="FastAPI")

    resp = await client.get(PUBLIC_LIST, params={"category": "Backend"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "backend-1"


@pytest.mark.asyncio
async def test_list_filter_featured(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="feat", featured=True)
    await _seed(db_session, slug="non-feat", featured=False)

    resp = await client.get(PUBLIC_LIST, params={"featured": "true"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "feat"


@pytest.mark.asyncio
async def test_list_items_do_not_include_body(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Body must be excluded from list responses."""
    await _seed(db_session, slug="no-body")
    resp = await client.get(PUBLIC_LIST)
    assert "body" not in resp.json()["items"][0]


@pytest.mark.asyncio
async def test_list_items_include_tags(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="tagged", tags=["fastapi", "python"])
    resp = await client.get(PUBLIC_LIST)
    assert resp.json()["items"][0]["tags"] == ["fastapi", "python"]


# ── Public detail ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_detail_returns_published_article(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="my-article")
    resp = await client.get(f"{PUBLIC_LIST}/my-article")
    assert resp.status_code == 200
    body = resp.json()
    assert body["slug"] == "my-article"
    assert "body" in body  # body is included in detail


@pytest.mark.asyncio
async def test_detail_draft_returns_404(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Draft articles must not be accessible via the public endpoint."""
    await _seed(db_session, slug="hidden-draft", status=ArticleStatus.DRAFT)
    resp = await client.get(f"{PUBLIC_LIST}/hidden-draft")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_detail_archived_returns_404(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await _seed(db_session, slug="archived-art", status=ArticleStatus.ARCHIVED)
    resp = await client.get(f"{PUBLIC_LIST}/archived-art")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_detail_nonexistent_returns_404(client: AsyncClient) -> None:
    resp = await client.get(f"{PUBLIC_LIST}/does-not-exist")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_detail_and_draft_return_same_404_body(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """404 response must be identical for missing vs draft — no status leakage."""
    await _seed(db_session, slug="is-draft", status=ArticleStatus.DRAFT)
    draft_resp = await client.get(f"{PUBLIC_LIST}/is-draft")
    missing_resp = await client.get(f"{PUBLIC_LIST}/definitely-missing")
    assert draft_resp.status_code == 404
    assert missing_resp.status_code == 404
    assert draft_resp.json() == missing_resp.json()
