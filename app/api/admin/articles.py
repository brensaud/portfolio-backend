"""
Admin article endpoints.

All routes are mounted under /admin/api/articles.
The get_current_admin dependency is applied at the router level in
app/api/admin/router.py — every endpoint here is automatically protected.

Endpoint summary:
  GET    /admin/api/articles              — paginated list (all statuses)
  POST   /admin/api/articles              — create draft
  GET    /admin/api/articles/{id}         — full article for editor
  PUT    /admin/api/articles/{id}         — update content
  PATCH  /admin/api/articles/{id}/publish      — publish
  PATCH  /admin/api/articles/{id}/unpublish    — unpublish → draft
  PATCH  /admin/api/articles/{id}/archive      — archive
  DELETE /admin/api/articles/{id}         — hard delete
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import get_current_admin
from app.db.session import get_db
from app.models.article import ArticleStatus
from app.schemas.admin.article import (
    AdminArticleDetail,
    AdminArticlesPage,
    ArticleCreate,
    ArticleUpdate,
)
from app.schemas.errors import ErrorResponse
from app.services.admin_article_service import AdminArticleService

logger = logging.getLogger(__name__)
router = APIRouter()

SortOrder = Literal["created_at_desc", "created_at_asc", "published_at_desc"]

_Responses = dict[int | str, dict[str, Any]]
_NOT_FOUND: _Responses = {404: {"model": ErrorResponse, "description": "Article not found"}}
_UNAUTH:    _Responses = {401: {"model": ErrorResponse, "description": "Authentication required"}}


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else None


def _get_service(db: AsyncSession = Depends(get_db)) -> AdminArticleService:
    return AdminArticleService(db)


# ── List ──────────────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=AdminArticlesPage,
    summary="Admin list articles",
    responses={**_UNAUTH},
)
async def list_articles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: ArticleStatus | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
    sort: SortOrder = Query(default="created_at_desc"),
    service: AdminArticleService = Depends(_get_service),
    _admin: str = Depends(get_current_admin),
) -> AdminArticlesPage:
    """Return all articles (all statuses) with optional filtering and search."""
    clean_search = (search.strip() or None) if search else None
    return await service.list_articles(
        page=page,
        page_size=page_size,
        status=status,
        search=clean_search,
        sort_by=sort,
    )


# ── Create ────────────────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=AdminArticleDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create draft article",
    responses={**_UNAUTH},
)
async def create_article(
    payload: ArticleCreate,
    request: Request,
    service: AdminArticleService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminArticleDetail:
    """Create a new draft article. Slug is auto-generated from the title."""
    return await service.create_article(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )


# ── Detail ────────────────────────────────────────────────────────────────────


@router.get(
    "/{article_id}",
    response_model=AdminArticleDetail,
    summary="Get article for editor",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def get_article(
    article_id: uuid.UUID,
    service: AdminArticleService = Depends(_get_service),
    _admin: str = Depends(get_current_admin),
) -> AdminArticleDetail:
    try:
        return await service.get_article(article_id)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.") from None


# ── Update ────────────────────────────────────────────────────────────────────


@router.put(
    "/{article_id}",
    response_model=AdminArticleDetail,
    summary="Update article content",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def update_article(
    article_id: uuid.UUID,
    payload: ArticleUpdate,
    request: Request,
    service: AdminArticleService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminArticleDetail:
    try:
        return await service.update_article(
            article_id,
            payload,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.") from None


# ── Status mutations ──────────────────────────────────────────────────────────


@router.patch(
    "/{article_id}/publish",
    response_model=AdminArticleDetail,
    summary="Publish article",
    responses={**_UNAUTH, **_NOT_FOUND,
               422: {"model": ErrorResponse, "description": "Missing required fields"}},
)
async def publish_article(
    article_id: uuid.UUID,
    request: Request,
    service: AdminArticleService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminArticleDetail:
    try:
        return await service.publish_article(
            article_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.") from None
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from None


@router.patch(
    "/{article_id}/unpublish",
    response_model=AdminArticleDetail,
    summary="Unpublish article (back to draft)",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def unpublish_article(
    article_id: uuid.UUID,
    request: Request,
    service: AdminArticleService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminArticleDetail:
    try:
        return await service.unpublish_article(
            article_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.") from None


@router.patch(
    "/{article_id}/archive",
    response_model=AdminArticleDetail,
    summary="Archive article",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def archive_article(
    article_id: uuid.UUID,
    request: Request,
    service: AdminArticleService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminArticleDetail:
    try:
        return await service.archive_article(
            article_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.") from None


# ── Delete ────────────────────────────────────────────────────────────────────


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete article permanently",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def delete_article(
    article_id: uuid.UUID,
    request: Request,
    service: AdminArticleService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> None:
    try:
        await service.delete_article(
            article_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Article not found.") from None
