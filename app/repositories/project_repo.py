"""
ProjectRepository — data access layer for projects.

Public methods:
  list_public()         — published projects only, ordered by display_order
  get_by_slug_public()  — single published project by slug (None if missing/unpublished)

Admin methods:
  list_admin()          — all statuses, paginated + searchable
  get_by_id()           — single project by primary key
  slug_exists()         — uniqueness check before create/update
  create()              — persist new draft
  update()              — update editable fields
  update_status()       — change status (publish/unpublish/archive)
  update_feature()      — toggle is_featured
  reorder()             — bulk-update display_order
  delete()              — hard delete (caller writes audit log first)

All methods: no commit — the service layer owns the transaction boundary.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus

logger = logging.getLogger(__name__)


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Public queries ────────────────────────────────────────────────────────

    async def list_public(
        self,
        *,
        page: int = 1,
        page_size: int = 12,
        category: str | None = None,
        featured: bool | None = None,
    ) -> tuple[list[Project], int]:
        """Return published projects only, ordered by display_order ascending."""
        base = select(Project).where(Project.status == ProjectStatus.PUBLISHED)

        if category is not None:
            base = base.where(Project.category == category)
        if featured is not None:
            base = base.where(Project.is_featured == featured)

        count_stmt = select(func.count()).select_from(base.subquery())
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        items_stmt = (
            base
            .order_by(Project.display_order.asc(), Project.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(items_stmt)
        return list(result.scalars().all()), total

    async def get_by_slug_public(self, slug: str) -> Project | None:
        """Return a published project by slug, or None (no status leakage)."""
        stmt = (
            select(Project)
            .where(Project.slug == slug)
            .where(Project.status == ProjectStatus.PUBLISHED)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Admin queries ─────────────────────────────────────────────────────────

    async def list_admin(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: ProjectStatus | None = None,
        search: str | None = None,
        sort_by: str = "display_order_asc",
    ) -> tuple[list[Project], int]:
        """Return all projects for admin, with optional filtering and search."""
        base = select(Project)

        if status is not None:
            base = base.where(Project.status == status)

        if search:
            pattern = f"%{search}%"
            base = base.where(
                or_(
                    Project.title.ilike(pattern),
                    Project.description.ilike(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        order_col = {
            "display_order_asc":  Project.display_order.asc(),
            "created_at_desc":    Project.created_at.desc(),
            "created_at_asc":     Project.created_at.asc(),
        }.get(sort_by, Project.display_order.asc())

        items_stmt = (
            base
            .order_by(order_col, Project.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(items_stmt)
        return list(result.scalars().all()), total

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """Return a single project by primary key, or None."""
        stmt = select(Project).where(Project.id == project_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def slug_exists(
        self,
        slug: str,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        """Return True if the slug is already in use."""
        stmt = select(Project.id).where(Project.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Project.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        *,
        slug: str,
        title: str,
        subtitle: str | None,
        description: str,
        category: str,
        tech_stack: list[str],
        is_featured: bool,
        display_order: int,
        links: list[dict],
        thumbnail_url: str | None,
    ) -> Project:
        """Persist a new draft project. Does NOT commit."""
        project = Project(
            slug=slug,
            title=title,
            subtitle=subtitle,
            description=description,
            category=category,
            status=ProjectStatus.DRAFT,
            tech_stack=tech_stack,
            is_featured=is_featured,
            display_order=display_order,
            links=links,
            thumbnail_url=thumbnail_url,
        )
        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)
        logger.debug("Project created id=%s slug=%r", project.id, slug)
        return project

    async def update(
        self,
        project: Project,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        description: str | None = None,
        category: str | None = None,
        tech_stack: list[str] | None = None,
        is_featured: bool | None = None,
        display_order: int | None = None,
        links: list[dict] | None = None,
        thumbnail_url: str | None = None,
        _clear_thumbnail: bool = False,
    ) -> Project:
        """Apply field-level updates. Does NOT commit."""
        if title is not None:
            project.title = title
        if subtitle is not None:
            project.subtitle = subtitle
        if description is not None:
            project.description = description
        if category is not None:
            project.category = category
        if tech_stack is not None:
            project.tech_stack = tech_stack
        if is_featured is not None:
            project.is_featured = is_featured
        if display_order is not None:
            project.display_order = display_order
        if links is not None:
            project.links = links
        if thumbnail_url is not None:
            project.thumbnail_url = thumbnail_url
        elif _clear_thumbnail:
            project.thumbnail_url = None

        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def update_status(
        self,
        project: Project,
        new_status: ProjectStatus,
    ) -> Project:
        """Change status. Does NOT commit."""
        project.status = new_status
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def update_feature(self, project: Project, is_featured: bool) -> Project:
        """Toggle is_featured. Does NOT commit."""
        project.is_featured = is_featured
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def reorder(self, items: list[dict]) -> None:
        """
        Bulk-update display_order for multiple projects atomically.

        items: [{"id": uuid, "display_order": int}, ...]
        Does NOT commit — caller owns the transaction.
        """
        for item in items:
            stmt = (
                update(Project)
                .where(Project.id == item["id"])
                .values(display_order=item["display_order"])
            )
            await self._session.execute(stmt)
        await self._session.flush()

    async def delete(self, project: Project) -> None:
        """Hard-delete. Does NOT commit."""
        await self._session.delete(project)
        await self._session.flush()
