"""Business logic for the Case Studies CMS."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction
from app.repositories.audit_repo import AuditRepository
from app.repositories.case_study_repo import CaseStudyRepository
from app.schemas.admin.case_study import AdminCaseStudyCreate, AdminCaseStudyUpdate
from app.schemas.case_study import CaseStudyPublic
from app.schemas.admin.case_study import AdminCaseStudyOut


class CaseStudyService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = CaseStudyRepository(db)
        self._audit = AuditRepository(db)

    # ── public ────────────────────────────────────────────────────────────────

    async def get_public_by_slug(self, slug: str) -> CaseStudyPublic | None:
        cs = await self._repo.get_published_by_slug(slug)
        if cs is None:
            return None
        return CaseStudyPublic.model_validate(cs)

    # ── admin reads ───────────────────────────────────────────────────────────

    async def list_all(self) -> list[AdminCaseStudyOut]:
        rows = await self._repo.list_all()
        return [AdminCaseStudyOut.model_validate(r) for r in rows]

    async def get_admin_by_id(self, id: uuid.UUID) -> AdminCaseStudyOut:
        cs = await self._repo.get_by_id(id)
        if cs is None:
            raise LookupError(f"Case study {id} not found")
        return AdminCaseStudyOut.model_validate(cs)

    # ── admin mutations ───────────────────────────────────────────────────────

    async def create(
        self,
        payload: AdminCaseStudyCreate,
        *,
        admin_username: str,
        client_ip: str,
    ) -> AdminCaseStudyOut:
        cs = await self._repo.create(
            slug=payload.slug,
            disclaimer=payload.disclaimer,
            content=payload.content,
        )
        await self._audit.write(
            action=AuditAction.CREATE,
            resource="case_study",
            resource_id=str(cs.id),
            admin_username=admin_username,
            client_ip=client_ip,
            detail={"slug": cs.slug},
        )
        await self._db.commit()
        await self._db.refresh(cs)
        return AdminCaseStudyOut.model_validate(cs)

    async def update(
        self,
        id: uuid.UUID,
        payload: AdminCaseStudyUpdate,
        *,
        admin_username: str,
        client_ip: str,
    ) -> AdminCaseStudyOut:
        cs = await self._repo.get_by_id(id)
        if cs is None:
            raise LookupError(f"Case study {id} not found")
        changed = payload.model_dump(exclude_unset=True)
        await self._repo.update(cs, **changed)
        await self._audit.write(
            action=AuditAction.UPDATE,
            resource="case_study",
            resource_id=str(cs.id),
            admin_username=admin_username,
            client_ip=client_ip,
            detail={"fields": list(changed.keys())},
        )
        await self._db.commit()
        await self._db.refresh(cs)
        return AdminCaseStudyOut.model_validate(cs)

    async def publish(
        self,
        id: uuid.UUID,
        *,
        admin_username: str,
        client_ip: str,
    ) -> AdminCaseStudyOut:
        cs = await self._repo.get_by_id(id)
        if cs is None:
            raise LookupError(f"Case study {id} not found")
        await self._repo.publish(cs)
        await self._audit.write(
            action=AuditAction.UPDATE,
            resource="case_study",
            resource_id=str(cs.id),
            admin_username=admin_username,
            client_ip=client_ip,
            detail={"status": "published"},
        )
        await self._db.commit()
        await self._db.refresh(cs)
        return AdminCaseStudyOut.model_validate(cs)

    async def unpublish(
        self,
        id: uuid.UUID,
        *,
        admin_username: str,
        client_ip: str,
    ) -> AdminCaseStudyOut:
        cs = await self._repo.get_by_id(id)
        if cs is None:
            raise LookupError(f"Case study {id} not found")
        await self._repo.unpublish(cs)
        await self._audit.write(
            action=AuditAction.UPDATE,
            resource="case_study",
            resource_id=str(cs.id),
            admin_username=admin_username,
            client_ip=client_ip,
            detail={"status": "draft"},
        )
        await self._db.commit()
        await self._db.refresh(cs)
        return AdminCaseStudyOut.model_validate(cs)

    async def delete(
        self,
        id: uuid.UUID,
        *,
        admin_username: str,
        client_ip: str,
    ) -> None:
        cs = await self._repo.get_by_id(id)
        if cs is None:
            raise LookupError(f"Case study {id} not found")
        slug = cs.slug
        await self._repo.delete(cs)
        await self._audit.write(
            action=AuditAction.DELETE,
            resource="case_study",
            resource_id=str(id),
            admin_username=admin_username,
            client_ip=client_ip,
            detail={"slug": slug},
        )
        await self._db.commit()
