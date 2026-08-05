"""
Public resume endpoint.

  GET /api/v1/resume — returns the full structured resume.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.resume import ResumePublic
from app.services.resume_service import ResumeService

router = APIRouter()


def _get_service(db: AsyncSession = Depends(get_db)) -> ResumeService:
    return ResumeService(db)


@router.get(
    "/resume",
    response_model=ResumePublic,
    summary="Get public resume",
)
async def get_resume(
    service: ResumeService = Depends(_get_service),
) -> ResumePublic:
    return await service.get_public()
