"""
Admin resume endpoints.

  GET    /admin/api/resume                          — full resume for editing
  PUT    /admin/api/resume/profile                  — update headline + summary
  POST   /admin/api/resume/experience               — add experience entry
  PUT    /admin/api/resume/experience/{id}          — update experience entry
  DELETE /admin/api/resume/experience/{id}          — delete experience entry
  POST   /admin/api/resume/skills                   — add skill group
  PUT    /admin/api/resume/skills/{id}              — update skill group
  DELETE /admin/api/resume/skills/{id}              — delete skill group
  POST   /admin/api/resume/education                — add education entry
  PUT    /admin/api/resume/education/{id}           — update education entry
  DELETE /admin/api/resume/education/{id}           — delete education entry
  POST   /admin/api/resume/certifications           — add certification
  PUT    /admin/api/resume/certifications/{id}      — update certification
  DELETE /admin/api/resume/certifications/{id}      — delete certification
"""

from __future__ import annotations

import logging
import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_deps import get_current_admin
from app.db.session import get_db
from app.schemas.admin.resume import (
    AdminResumeCertificationOut,
    AdminResumeEducationOut,
    AdminResumeExperienceOut,
    AdminResumeOut,
    AdminResumeProfileOut,
    AdminResumeSkillGroupOut,
    ResumeCertificationCreate,
    ResumeCertificationUpdate,
    ResumeEducationCreate,
    ResumeEducationUpdate,
    ResumeExperienceCreate,
    ResumeExperienceUpdate,
    ResumeProfileUpdate,
    ResumeSkillGroupCreate,
    ResumeSkillGroupUpdate,
)
from app.services.resume_service import ResumeService

logger = logging.getLogger(__name__)
router = APIRouter()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else None


def _get_service(db: AsyncSession = Depends(get_db)) -> ResumeService:
    return ResumeService(db)


# ── Full resume ───────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=AdminResumeOut,
    summary="Get full resume (admin)",
)
async def get_admin_resume(
    service: ResumeService = Depends(_get_service),
    _admin: str = Depends(get_current_admin),
) -> AdminResumeOut:
    return await service.get_admin()


# ── Profile ───────────────────────────────────────────────────────────────────


@router.put(
    "/profile",
    response_model=AdminResumeProfileOut,
    summary="Update resume profile (headline + summary)",
)
async def update_profile(
    payload: ResumeProfileUpdate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeProfileOut:
    return await service.update_profile(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )


# ── Experience ────────────────────────────────────────────────────────────────


@router.post(
    "/experience",
    response_model=AdminResumeExperienceOut,
    status_code=HTTPStatus.CREATED,
    summary="Add experience entry",
)
async def create_experience(
    payload: ResumeExperienceCreate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeExperienceOut:
    return await service.create_experience(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )


@router.put(
    "/experience/{id}",
    response_model=AdminResumeExperienceOut,
    summary="Update experience entry",
)
async def update_experience(
    id: uuid.UUID,
    payload: ResumeExperienceUpdate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeExperienceOut:
    try:
        return await service.update_experience(
            id,
            payload,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/experience/{id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete experience entry",
)
async def delete_experience(
    id: uuid.UUID,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> None:
    try:
        await service.delete_experience(
            id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Skill groups ──────────────────────────────────────────────────────────────


@router.post(
    "/skills",
    response_model=AdminResumeSkillGroupOut,
    status_code=HTTPStatus.CREATED,
    summary="Add skill group",
)
async def create_skill_group(
    payload: ResumeSkillGroupCreate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeSkillGroupOut:
    return await service.create_skill_group(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )


@router.put(
    "/skills/{id}",
    response_model=AdminResumeSkillGroupOut,
    summary="Update skill group",
)
async def update_skill_group(
    id: uuid.UUID,
    payload: ResumeSkillGroupUpdate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeSkillGroupOut:
    try:
        return await service.update_skill_group(
            id,
            payload,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/skills/{id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete skill group",
)
async def delete_skill_group(
    id: uuid.UUID,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> None:
    try:
        await service.delete_skill_group(
            id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Education ─────────────────────────────────────────────────────────────────


@router.post(
    "/education",
    response_model=AdminResumeEducationOut,
    status_code=HTTPStatus.CREATED,
    summary="Add education entry",
)
async def create_education(
    payload: ResumeEducationCreate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeEducationOut:
    return await service.create_education(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )


@router.put(
    "/education/{id}",
    response_model=AdminResumeEducationOut,
    summary="Update education entry",
)
async def update_education(
    id: uuid.UUID,
    payload: ResumeEducationUpdate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeEducationOut:
    try:
        return await service.update_education(
            id,
            payload,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/education/{id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete education entry",
)
async def delete_education(
    id: uuid.UUID,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> None:
    try:
        await service.delete_education(
            id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Certifications ────────────────────────────────────────────────────────────


@router.post(
    "/certifications",
    response_model=AdminResumeCertificationOut,
    status_code=HTTPStatus.CREATED,
    summary="Add certification",
)
async def create_certification(
    payload: ResumeCertificationCreate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeCertificationOut:
    return await service.create_certification(
        payload,
        actor=admin,
        ip_address=_client_ip(request),
    )


@router.put(
    "/certifications/{id}",
    response_model=AdminResumeCertificationOut,
    summary="Update certification",
)
async def update_certification(
    id: uuid.UUID,
    payload: ResumeCertificationUpdate,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> AdminResumeCertificationOut:
    try:
        return await service.update_certification(
            id,
            payload,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/certifications/{id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete certification",
)
async def delete_certification(
    id: uuid.UUID,
    request: Request,
    service: ResumeService = Depends(_get_service),
    admin: str = Depends(get_current_admin),
) -> None:
    try:
        await service.delete_certification(
            id,
            actor=admin,
            ip_address=_client_ip(request),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
