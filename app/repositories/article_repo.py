"""
ArticleRepository — data access layer for articles.

Public methods:
  list_public()         — published articles only, paginated + filtered
  get_by_slug_public()  — single published article by slug (None if not found or not published)

Admin methods:
  list_admin()          — all statuses, paginated + searchable
  get_by_id()           — single article by primary key
  slug_exists()         — check uniqueness before create/update
  create()              — persist new draft
  update()              — update editable fields
  update_status()       — change status (publish/unpublish/archive)
  delete()              — hard delete (caller writes audit log first)

All methods: no commit — the service layer owns the transaction boundary.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleStatus

logger = logging.getLogger(__name__)


class ArticleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Public queries ────────────────────────────────────────────────────────

    async def list_public(
        self,
        *,
        page: int = 1,
        page_size: int = 12,
        category: str | None = None,
        featured: bool | None = None,
    ) -> tuple[list[Article], int]:
        """
        Return published articles only, ordered newest first.

        Security: status=published is always enforced here — cannot be
        bypassed by any caller. Draft and archived articles are never returned.
        """
        base = (
            select(Article)
            .where(Article.status == ArticleStatus.PUBLISHED)
        )

        if category is not None:
            base = base.where(Article.category == category)
        if featured is not None:
            base = base.where(Article.featured == featured)

        count_stmt = select(func.count()).select_from(base.subquery())
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        items_stmt = (
            base
            .order_by(Article.published_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(items_stmt)
        return list(result.scalars().all()), total

    async def get_by_slug_public(self, slug: str) -> Article | None:
        """
        Return a published article by slug, or None.

        Returns None for both "not found" and "not published" so callers
        cannot distinguish between the two — no status leakage to the public.
        """
        stmt = (
            select(Article)
            .where(Article.slug == slug)
            .where(Article.status == ArticleStatus.PUBLISHED)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Admin queries ─────────────────────────────────────────────────────────

    async def list_admin(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: ArticleStatus | None = None,
        search: str | None = None,
        sort_by: str = "created_at_desc",
    ) -> tuple[list[Article], int]:
        """
        Return all articles for admin consumption, with optional filtering.

        sort_by values:
          created_at_desc   — newest created first (default)
          created_at_asc    — oldest created first
          published_at_desc — most recently published first
        """
        base = select(Article)

        if status is not None:
            base = base.where(Article.status == status)

        if search:
            pattern = f"%{search}%"
            base = base.where(
                or_(
                    Article.title.ilike(pattern),
                    Article.summary.ilike(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        order_col = {
            "created_at_asc":    Article.created_at.asc(),
            "published_at_desc": Article.published_at.desc().nulls_last(),
        }.get(sort_by, Article.created_at.desc())

        items_stmt = (
            base
            .order_by(order_col)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(items_stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, article_id: uuid.UUID) -> Article | None:
        """Return a single article by primary key, or None."""
        stmt = select(Article).where(Article.id == article_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def slug_exists(
        self,
        slug: str,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        """
        Return True if the slug is already taken.

        exclude_id allows checking uniqueness during an update without
        matching the article being updated.
        """
        stmt = select(Article.id).where(Article.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Article.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        *,
        slug: str,
        title: str,
        summary: str,
        body: str | None,
        category: str,
        tags: list[str],
        featured: bool,
        reading_time_minutes: int | None,
    ) -> Article:
        """Persist a new draft article. Does NOT commit."""
        article = Article(
            slug=slug,
            title=title,
            summary=summary,
            body=body,
            category=category,
            status=ArticleStatus.DRAFT,
            tags=tags,
            featured=featured,
            reading_time_minutes=reading_time_minutes,
        )
        self._session.add(article)
        await self._session.flush()
        await self._session.refresh(article)

        logger.debug("Article created id=%s slug=%r", article.id, slug)
        return article

    async def update(
        self,
        article: Article,
        *,
        title: str | None = None,
        summary: str | None = None,
        body: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        featured: bool | None = None,
        reading_time_minutes: int | None = None,
    ) -> Article:
        """Apply field-level updates. Does NOT commit."""
        if title is not None:
            article.title = title
        if summary is not None:
            article.summary = summary
        if body is not None:
            article.body = body
        if category is not None:
            article.category = category
        if tags is not None:
            article.tags = tags
        if featured is not None:
            article.featured = featured
        if reading_time_minutes is not None:
            article.reading_time_minutes = reading_time_minutes

        await self._session.flush()
        await self._session.refresh(article)
        return article

    async def update_status(
        self,
        article: Article,
        status: ArticleStatus,
        *,
        published_at: datetime | None = None,
    ) -> Article:
        """
        Change the article status. Does NOT commit.

        published_at is passed by the service when transitioning to PUBLISHED
        so the first-publish timestamp is set exactly once.
        """
        article.status = status
        if published_at is not None:
            article.published_at = published_at

        await self._session.flush()
        await self._session.refresh(article)

        logger.debug("Article id=%s status → %s", article.id, status)
        return article

    async def delete(self, article: Article) -> None:
        """
        Hard-delete an article row. Does NOT commit.

        The caller (AdminArticleService) must write an audit entry in the
        same transaction before calling this method.
        """
        await self._session.delete(article)
        await self._session.flush()
        logger.debug("Article id=%s deleted", article.id)
