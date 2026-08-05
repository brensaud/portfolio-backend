"""
Public project endpoints.

  GET /api/v1/projects          — paginated list of published projects
  GET /api/v1/projects/{slug}   — full project by slug (published only)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.errors import ErrorResponse
from app.schemas.project import ProjectPublic, ProjectsPage
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])

_NOT_FOUND = {404: {"model": ErrorResponse, "description": "Project not found"}}


def _get_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.get(
    "",
    response_model=ProjectsPage,
    summary="List published projects",
)
async def list_projects(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    category: str | None = Query(default=None, max_length=50),
    featured: bool | None = Query(default=None),
    service: ProjectService = Depends(_get_service),
) -> ProjectsPage:
    """Return a paginated list of published projects ordered by display_order."""
    return await service.list_projects(
        page=page,
        page_size=page_size,
        category=category,
        featured=featured,
    )


@router.get(
    "/{slug}",
    response_model=ProjectPublic,
    summary="Get project by slug",
    responses={**_NOT_FOUND},
)
async def get_project(
    slug: str,
    service: ProjectService = Depends(_get_service),
) -> ProjectPublic:
    """
    Return a published project by slug.

    Returns 404 for both non-existent and non-published slugs.
    """
    try:
        return await service.get_project(slug)
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        ) from None
