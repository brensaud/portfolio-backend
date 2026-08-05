"""
Admin case study endpoints.

  GET    /admin/api/case-studies              — list all case studies
  POST   /admin/api/case-studies              — create a case study
  GET    /admin/api/case-studies/{id}         — get one case study
  PUT    /admin/api/case-studies/{id}         — update a case study
  PATCH  /admin/api/case-studies/{id}/publish — publish
  PATCH  /admin/api/case-studies/{id}/unpublish — unpublish
  DELETE /admin/api/case-studies/{id}         — delete
"""

from __future__ import annotations

import logging
import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import get_current_admin
from app.db.session import get_db
from app.schemas.admin.case_study import (
    AdminCaseStudyCreate,
    AdminCaseStudyOut,
    AdminCaseStudyUpdate,
)
from app.services.case_study_service import CaseStudyService

logger = logging.getLogger(__name__)
router = APIRouter()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else None


def _get_service(db: AsyncSession = Depends(get_db)) -> CaseStudyService:
    return CaseStudyService(db)


_protected = APIRouter(dependencies=[Depends(get_current_admin)])


# ── list / create ─────────────────────────────────────────────────────────────

@_protected.get(
    "",
    response_model=list[AdminCaseStudyOut],
    summary="List all case studies",
)
async def list_case_studies(
    service: CaseStudyService = Depends(_get_service),
) -> list[AdminCaseStudyOut]:
    return await service.list_all()


@_protected.post(
    "",
    response_model=AdminCaseStudyOut,
    status_code=HTTPStatus.CREATED,
    summary="Create a case study",
)
async def create_case_study(
    payload: AdminCaseStudyCreate,
    request: Request,
    admin: str = Depends(get_current_admin),
    service: CaseStudyService = Depends(_get_service),
) -> AdminCaseStudyOut:
    try:
        return await service.create(
            payload,
            admin_username=admin,
            client_ip=_client_ip(request) or "unknown",
        )
    except Exception as exc:
        logger.exception("Failed to create case study")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ── single item ───────────────────────────────────────────────────────────────

@_protected.get(
    "/{id}",
    response_model=AdminCaseStudyOut,
    summary="Get a case study",
)
async def get_case_study(
    id: uuid.UUID,
    service: CaseStudyService = Depends(_get_service),
) -> AdminCaseStudyOut:
    try:
        return await service.get_admin_by_id(id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@_protected.put(
    "/{id}",
    response_model=AdminCaseStudyOut,
    summary="Update a case study",
)
async def update_case_study(
    id: uuid.UUID,
    payload: AdminCaseStudyUpdate,
    request: Request,
    admin: str = Depends(get_current_admin),
    service: CaseStudyService = Depends(_get_service),
) -> AdminCaseStudyOut:
    try:
        return await service.update(
            id,
            payload,
            admin_username=admin,
            client_ip=_client_ip(request) or "unknown",
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@_protected.patch(
    "/{id}/publish",
    response_model=AdminCaseStudyOut,
    summary="Publish a case study",
)
async def publish_case_study(
    id: uuid.UUID,
    request: Request,
    admin: str = Depends(get_current_admin),
    service: CaseStudyService = Depends(_get_service),
) -> AdminCaseStudyOut:
    try:
        return await service.publish(
            id,
            admin_username=admin,
            client_ip=_client_ip(request) or "unknown",
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@_protected.patch(
    "/{id}/unpublish",
    response_model=AdminCaseStudyOut,
    summary="Unpublish a case study",
)
async def unpublish_case_study(
    id: uuid.UUID,
    request: Request,
    admin: str = Depends(get_current_admin),
    service: CaseStudyService = Depends(_get_service),
) -> AdminCaseStudyOut:
    try:
        return await service.unpublish(
            id,
            admin_username=admin,
            client_ip=_client_ip(request) or "unknown",
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@_protected.delete(
    "/{id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete a case study",
)
async def delete_case_study(
    id: uuid.UUID,
    request: Request,
    admin: str = Depends(get_current_admin),
    service: CaseStudyService = Depends(_get_service),
) -> None:
    try:
        await service.delete(
            id,
            admin_username=admin,
            client_ip=_client_ip(request) or "unknown",
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── attach protected sub-router to public router ──────────────────────────────

router.include_router(_protected)
