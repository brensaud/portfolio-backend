"""
AdminProjectService — business logic for admin project management.

Responsibilities:
  1. List projects (all statuses) with pagination, filtering, search.
  2. Fetch a single project for the editor.
  3. Create a new draft.
  4. Update editable fields.
  5. Publish, unpublish, archive.
  6. Toggle is_featured.
  7. Reorder (bulk display_order update).
  8. Delete with pre-delete audit log.

Design:
  • Service owns every transaction boundary (commit).
  • Repository only flushes.
  • Publish requires title + description + category — service raises ValueError.
  • Slug auto-generated from title on create; unchanged on update.
  • is_featured is a multi-select flag; no uniqueness enforcement.
  • Reorder validates all IDs exist before any update.
"""

from __future__ import annotations

import logging
import math
import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import ProjectStatus
from app.repositories.audit_repo import AuditRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.admin.project import (
    AdminProjectDetail,
    AdminProjectsPage,
    AdminProjectSummary,
    ProjectCreate,
    ProjectReorderRequest,
    ProjectUpdate,
)

logger = logging.getLogger(__name__)

_ACTION_CREATED   = "admin.project.created"
_ACTION_UPDATED   = "admin.project.updated"
_ACTION_PUBLISHED = "admin.project.published"
_ACTION_UNPUBLISHED = "admin.project.unpublished"
_ACTION_ARCHIVED  = "admin.project.archived"
_ACTION_FEATURED  = "admin.project.feature_toggled"
_ACTION_REORDERED = "admin.project.reordered"
_ACTION_DELETED   = "admin.project.deleted"

_RESOURCE_TYPE = "project"


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = re.sub(r"^-+|-+$", "", slug)
    return slug[:200]


class AdminProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo    = ProjectRepository(session)
        self._audit   = AuditRepository(session)

    # ── List ──────────────────────────────────────────────────────────────────

    async def list_projects(
        self,
        *,
        page: int,
        page_size: int,
        status: ProjectStatus | None,
        search: str | None,
        sort_by: str,
    ) -> AdminProjectsPage:
        items, total = await self._repo.list_admin(
            page=page,
            page_size=page_size,
            status=status,
            search=search,
            sort_by=sort_by,
        )
        pages = math.ceil(total / page_size) if total > 0 else 0
        return AdminProjectsPage(
            items=[AdminProjectSummary.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    # ── Detail ────────────────────────────────────────────────────────────────

    async def get_project(self, project_id: uuid.UUID) -> AdminProjectDetail:
        """Raises LookupError if not found."""
        project = await self._repo.get_by_id(project_id)
        if project is None:
            raise LookupError(f"Project {project_id} not found.")
        return AdminProjectDetail.model_validate(project)

    # ── Create ────────────────────────────────────────────────────────────────

    async def create_project(
        self,
        data: ProjectCreate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminProjectDetail:
        """Create a new draft project. Slug is auto-generated from title."""
        base_slug = _slugify(data.title)
        slug = await self._unique_slug(base_slug)

        links_dicts = [lnk.model_dump() for lnk in data.links]

        project = await self._repo.create(
            slug=slug,
            title=data.title,
            subtitle=data.subtitle,
            description=data.description,
            category=data.category,
            tech_stack=data.tech_stack,
            is_featured=data.is_featured,
            display_order=data.display_order,
            links=links_dicts,
            thumbnail_url=data.thumbnail_url,
        )

        await self._audit.write(
            action=_ACTION_CREATED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(project.id),
            metadata={"slug": slug, "status": ProjectStatus.DRAFT},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info("Admin created project id=%s slug=%r actor=%s", project.id, slug, actor)
        return AdminProjectDetail.model_validate(project)

    # ── Update ────────────────────────────────────────────────────────────────

    async def update_project(
        self,
        project_id: uuid.UUID,
        data: ProjectUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminProjectDetail:
        """Update editable fields. Raises LookupError if not found."""
        project = await self._repo.get_by_id(project_id)
        if project is None:
            raise LookupError(f"Project {project_id} not found.")

        links_dicts = (
            [lnk.model_dump() for lnk in data.links]
            if data.links is not None
            else None
        )

        project = await self._repo.update(
            project,
            title=data.title,
            subtitle=data.subtitle,
            description=data.description,
            category=data.category,
            tech_stack=data.tech_stack,
            is_featured=data.is_featured,
            display_order=data.display_order,
            links=links_dicts,
            thumbnail_url=data.thumbnail_url,
            _clear_thumbnail=data.clear_thumbnail,
        )

        await self._audit.write(
            action=_ACTION_UPDATED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(project_id),
            metadata={"status": project.status},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info("Admin updated project id=%s actor=%s", project_id, actor)
        return AdminProjectDetail.model_validate(project)

    # ── Status mutations ──────────────────────────────────────────────────────

    async def publish_project(
        self,
        project_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminProjectDetail:
        """
        Transition → published.

        Raises:
            LookupError — not found.
            ValueError  — missing required fields (title, description, category).
        """
        project = await self._repo.get_by_id(project_id)
        if project is None:
            raise LookupError(f"Project {project_id} not found.")

        missing = [
            field for field, value in [
                ("title",       project.title),
                ("description", project.description),
                ("category",    project.category),
            ]
            if not value
        ]
        if missing:
            raise ValueError(
                f"Cannot publish: missing required fields: {', '.join(missing)}"
            )

        project = await self._repo.update_status(project, ProjectStatus.PUBLISHED)
        await self._audit.write(
            action=_ACTION_PUBLISHED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(project_id),
            metadata={"slug": project.slug},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info("Admin published project id=%s slug=%r actor=%s", project_id, project.slug, actor)
        return AdminProjectDetail.model_validate(project)

    async def unpublish_project(
        self,
        project_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminProjectDetail:
        """Transition → draft."""
        return await self._mutate_status(
            project_id,
            new_status=ProjectStatus.DRAFT,
            action=_ACTION_UNPUBLISHED,
            actor=actor,
            ip_address=ip_address,
        )

    async def archive_project(
        self,
        project_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminProjectDetail:
        """Transition → archived."""
        return await self._mutate_status(
            project_id,
            new_status=ProjectStatus.ARCHIVED,
            action=_ACTION_ARCHIVED,
            actor=actor,
            ip_address=ip_address,
        )

    async def _mutate_status(
        self,
        project_id: uuid.UUID,
        *,
        new_status: ProjectStatus,
        action: str,
        actor: str,
        ip_address: str | None,
    ) -> AdminProjectDetail:
        project = await self._repo.get_by_id(project_id)
        if project is None:
            raise LookupError(f"Project {project_id} not found.")
        previous = project.status
        project = await self._repo.update_status(project, new_status)
        await self._audit.write(
            action=action,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(project_id),
            metadata={"status_before": previous, "status_after": new_status},
            ip_address=ip_address,
        )
        await self._session.commit()
        logger.info("Admin %s project id=%s actor=%s", action, project_id, actor)
        return AdminProjectDetail.model_validate(project)

    # ── Feature toggle ────────────────────────────────────────────────────────

    async def toggle_feature(
        self,
        project_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminProjectDetail:
        """Toggle is_featured. Multiple projects may be featured simultaneously."""
        project = await self._repo.get_by_id(project_id)
        if project is None:
            raise LookupError(f"Project {project_id} not found.")

        new_featured = not project.is_featured
        project = await self._repo.update_feature(project, new_featured)
        await self._audit.write(
            action=_ACTION_FEATURED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(project_id),
            metadata={"is_featured": new_featured},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info("Admin toggled feature project id=%s is_featured=%s actor=%s", project_id, new_featured, actor)
        return AdminProjectDetail.model_validate(project)

    # ── Reorder ───────────────────────────────────────────────────────────────

    async def reorder_projects(
        self,
        data: ProjectReorderRequest,
        *,
        actor: str,
        ip_address: str | None,
    ) -> None:
        """
        Bulk-update display_order for the provided project IDs.

        Raises:
            ValueError — one or more IDs do not exist.
        """
        # Validate all IDs exist before writing anything
        for item in data.items:
            exists = await self._repo.get_by_id(item.id)
            if exists is None:
                raise ValueError(f"Project {item.id} not found.")

        items_dicts = [
            {"id": item.id, "display_order": item.display_order}
            for item in data.items
        ]
        await self._repo.reorder(items_dicts)

        await self._audit.write(
            action=_ACTION_REORDERED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=None,
            metadata={"count": len(data.items)},
            ip_address=ip_address,
        )
        await self._session.commit()

        logger.info("Admin reordered %d projects actor=%s", len(data.items), actor)

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete_project(
        self,
        project_id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> None:
        """Hard-delete. Audit log is written before deletion in the same transaction."""
        project = await self._repo.get_by_id(project_id)
        if project is None:
            raise LookupError(f"Project {project_id} not found.")

        await self._audit.write(
            action=_ACTION_DELETED,
            actor=actor,
            resource_type=_RESOURCE_TYPE,
            resource_id=str(project_id),
            metadata={"slug": project.slug, "status_at_delete": project.status},
            ip_address=ip_address,
        )
        await self._repo.delete(project)
        await self._session.commit()

        logger.info("Admin deleted project id=%s actor=%s", project_id, actor)

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _unique_slug(self, base: str) -> str:
        slug = base
        counter = 2
        while await self._repo.slug_exists(slug):
            slug = f"{base}-{counter}"
            counter += 1
        return slug
