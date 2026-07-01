"""
Health check endpoint.

GET /health

Returns the application status, version, and environment.
Also performs a lightweight database connectivity check so the
health endpoint can be used by Docker Compose healthchecks and
load balancers.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns application status and database connectivity.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Health check: database unreachable")
        db_status = "unreachable"

    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        database=db_status,
    )
