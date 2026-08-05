"""
ProjectService — public read-only business logic for the /work section.
"""

from __future__ import annotations

import math
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import ProjectStatus
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectPublic, ProjectListItem, ProjectsPage

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = ProjectRepository(session)

    async def list_projects(
        self,
        *,
        page: int,
        page_size: int,
        category: str | None,
        featured: bool | None,
    ) -> ProjectsPage:
        items, total = await self._repo.list_public(
            page=page,
            page_size=page_size,
            category=category,
            featured=featured,
        )
        pages = math.ceil(total / page_size) if total > 0 else 0
        return ProjectsPage(
            items=[ProjectListItem.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_project(self, slug: str) -> ProjectPublic:
        """Raises LookupError if not found or not published."""
        project = await self._repo.get_by_slug_public(slug)
        if project is None:
            raise LookupError(f"Project {slug!r} not found.")
        return ProjectPublic.model_validate(project)
