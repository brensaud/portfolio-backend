"""
Public case study endpoint.

  GET /api/v1/projects/{slug}/case-study — returns the published case study for a project slug.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.case_study import CaseStudyPublic
from app.services.case_study_service import CaseStudyService

router = APIRouter()


def _get_service(db: AsyncSession = Depends(get_db)) -> CaseStudyService:
    return CaseStudyService(db)


@router.get(
    "/projects/{slug}/case-study",
    response_model=CaseStudyPublic,
    summary="Get published case study for a project slug",
)
async def get_case_study(
    slug: str,
    service: CaseStudyService = Depends(_get_service),
) -> CaseStudyPublic:
    cs = await service.get_public_by_slug(slug)
    if cs is None:
        raise HTTPException(status_code=404, detail="Case study not found")
    return cs
