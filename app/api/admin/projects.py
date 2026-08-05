"""
Admin project endpoints.

All routes are mounted under /admin/api/projects.
The get_current_admin dependency is applied at the router level in
app/api/admin/router.py — every endpoint here is automatically protected.

Endpoint summary:
  GET    /admin/api/projects                   — paginated list (all statuses)
  POST   /admin/api/projects                   — create draft
  PATCH  /admin/api/projects/reorder           — bulk display_order update
  GET    /admin/api/projects/{id}              — project for editor
  PUT    /admin/api/projects/{id}              — update content
  PATCH  /admin/api/projects/{id}/publish      — publish
  PATCH  /admin/api/projects/{id}/unpublish    — unpublish → draft
  PATCH  /admin/api/projects/{id}/archive      — archive
  PATCH  /admin/api/projects/{id}/feature      — toggle is_featured
  DELETE /admin/api/projects/{id}              — hard delete
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import get_current_admin
from app.db.session import get_db
from app.models.project import ProjectStatus
from app.schemas.admin.project import (
    AdminProjectDetail,
    AdminProjectsPage,
    ProjectCreate,
    ProjectReorderRequest,
    ProjectUpdate,
)
from app.schemas.errors import ErrorResponse
from app.services.admin_project_service import AdminProjectService

logger = logging.getLogger(__name__)
router = APIRouter()

AdminSort = Literal["display_order_asc", "created_at_desc", "created_at_asc"]

_Responses = dict[int | str, dict[str, Any]]
_NOT_FOUND: _Responses = {404: {"model": ErrorResponse, "description": "Project not found"}}
_UNAUTH:    _Responses = {401: {"model": ErrorResponse, "description": "Authentication required"}}


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else None


def _get_service(db: AsyncSession = Depends(get_db)) -> AdminProjectService:
    return AdminProjectService(db)


# ── List ──────────────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=AdminProjectsPage,
    summary="Admin list projects",
    responses={**_UNAUTH},
)
async def list_projects(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: ProjectStatus | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
    sort: AdminSort = Query(default="display_order_asc"),
    service: AdminProjectService = Depends(_get_service),
    _admin: str = Depends(get_current_admin),
) -> AdminProjectsPage:
    clean_search = (search.strip() or None) if search else None
    return await service.list_projects(
        page=page,
        page_size=page_size,
        status=status,
        search=clean_search,
        sort_by=sort,
    )


# ── Create ────────────────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=AdminProjectDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create draft project",
    responses={**_UNAUTH},
)
async def create_project(
    payload: ProjectCreate,
    request: Request,
    service: AdminProjectService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminProjectDetail:
    return await service.create_project(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )


# ── Reorder (before {id} route to avoid ambiguity) ───────────────────────────


@router.patch(
    "/reorder",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Bulk-update display_order",
    responses={**_UNAUTH},
)
async def reorder_projects(
    payload: ProjectReorderRequest,
    request: Request,
    service: AdminProjectService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> None:
    try:
        await service.reorder_projects(
            payload,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from None


# ── Detail ────────────────────────────────────────────────────────────────────


@router.get(
    "/{project_id}",
    response_model=AdminProjectDetail,
    summary="Get project for editor",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def get_project(
    project_id: uuid.UUID,
    service: AdminProjectService = Depends(_get_service),
    _admin: str = Depends(get_current_admin),
) -> AdminProjectDetail:
    try:
        return await service.get_project(project_id)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.") from None


# ── Update ────────────────────────────────────────────────────────────────────


@router.put(
    "/{project_id}",
    response_model=AdminProjectDetail,
    summary="Update project",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    request: Request,
    service: AdminProjectService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminProjectDetail:
    try:
        return await service.update_project(
            project_id,
            payload,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.") from None


# ── Status mutations ──────────────────────────────────────────────────────────


@router.patch(
    "/{project_id}/publish",
    response_model=AdminProjectDetail,
    summary="Publish project",
    responses={**_UNAUTH, **_NOT_FOUND,
               422: {"model": ErrorResponse, "description": "Missing required fields"}},
)
async def publish_project(
    project_id: uuid.UUID,
    request: Request,
    service: AdminProjectService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminProjectDetail:
    try:
        return await service.publish_project(
            project_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.") from None
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from None


@router.patch(
    "/{project_id}/unpublish",
    response_model=AdminProjectDetail,
    summary="Unpublish project (back to draft)",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def unpublish_project(
    project_id: uuid.UUID,
    request: Request,
    service: AdminProjectService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminProjectDetail:
    try:
        return await service.unpublish_project(
            project_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.") from None


@router.patch(
    "/{project_id}/archive",
    response_model=AdminProjectDetail,
    summary="Archive project",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def archive_project(
    project_id: uuid.UUID,
    request: Request,
    service: AdminProjectService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminProjectDetail:
    try:
        return await service.archive_project(
            project_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.") from None


# ── Feature toggle ────────────────────────────────────────────────────────────


@router.patch(
    "/{project_id}/feature",
    response_model=AdminProjectDetail,
    summary="Toggle is_featured flag",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def toggle_feature(
    project_id: uuid.UUID,
    request: Request,
    service: AdminProjectService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminProjectDetail:
    try:
        return await service.toggle_feature(
            project_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.") from None


# ── Delete ────────────────────────────────────────────────────────────────────


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project permanently",
    responses={**_UNAUTH, **_NOT_FOUND},
)
async def delete_project(
    project_id: uuid.UUID,
    request: Request,
    service: AdminProjectService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> None:
    try:
        await service.delete_project(
            project_id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found.") from None
