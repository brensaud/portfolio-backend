"""
ArticleService — public read-only business logic for articles.

Responsibilities:
  1. List published articles with pagination and optional filters.
  2. Fetch a single published article by slug.

This service is intentionally minimal — no writes, no auth.
All admin operations are handled by AdminArticleService.
"""

from __future__ import annotations

import logging
import math

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticlePublic, ArticlesPage

logger = logging.getLogger(__name__)


class ArticleService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ArticleRepository(session)

    async def list_articles(
        self,
        *,
        page: int,
        page_size: int,
        category: str | None,
        featured: bool | None,
    ) -> ArticlesPage:
        """Return a paginated page of published articles."""
        items, total = await self._repo.list_public(
            page=page,
            page_size=page_size,
            category=category,
            featured=featured,
        )
        pages = math.ceil(total / page_size) if total > 0 else 0
        return ArticlesPage(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_article(self, slug: str) -> ArticlePublic:
        """
        Return a published article by slug.

        Raises:
            LookupError — if not found or not published (same exception,
                          so the route returns 404 in both cases without
                          leaking draft/archived status to the public).
        """
        article = await self._repo.get_by_slug_public(slug)
        if article is None:
            raise LookupError(f"Article '{slug}' not found.")
        return ArticlePublic.model_validate(article)
