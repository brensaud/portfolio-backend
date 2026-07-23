"""
Public article endpoints.

Endpoint summary:
  GET /api/v1/articles          — paginated list of published articles
  GET /api/v1/articles/{slug}   — full article by slug (published only)

These endpoints require no authentication.
Draft and archived articles are never returned — enforced at the
repository layer, not just the route layer.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.article import ArticlePublic, ArticlesPage
from app.schemas.errors import ErrorResponse
from app.services.article_service import ArticleService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["articles"])

_NOT_FOUND = {404: {"model": ErrorResponse, "description": "Article not found"}}


def _get_service(db: AsyncSession = Depends(get_db)) -> ArticleService:
    return ArticleService(db)


@router.get(
    "",
    response_model=ArticlesPage,
    summary="List published articles",
)
async def list_articles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    category: str | None = Query(default=None, max_length=50),
    featured: bool | None = Query(default=None),
    service: ArticleService = Depends(_get_service),
) -> ArticlesPage:
    """Return a paginated list of published articles. Draft and archived articles are excluded."""
    return await service.list_articles(
        page=page,
        page_size=page_size,
        category=category,
        featured=featured,
    )


@router.get(
    "/{slug}",
    response_model=ArticlePublic,
    summary="Get article by slug",
    responses={**_NOT_FOUND},
)
async def get_article(
    slug: str,
    service: ArticleService = Depends(_get_service),
) -> ArticlePublic:
    """
    Return a published article by slug.

    Returns 404 for both non-existent and non-published articles so
    the public cannot distinguish draft from missing.
    """
    try:
        return await service.get_article(slug)
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found.",
        ) from None
