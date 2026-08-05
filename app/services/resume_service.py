"""
ResumeService — business logic for resume CMS.

Used by both the public endpoint (read-only) and admin endpoints (CRUD).
All admin mutations write an audit log entry and commit.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_repo import AuditRepository
from app.repositories.resume_repo import ResumeRepository
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
from app.schemas.resume import (
    ResumeCertificationPublic,
    ResumeEducationPublic,
    ResumeExperiencePublic,
    ResumeProfilePublic,
    ResumePublic,
    ResumeSkillGroupPublic,
)

logger = logging.getLogger(__name__)

_RESOURCE = "resume"


class ResumeService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = ResumeRepository(session)
        self._audit = AuditRepository(session)

    # ── Public read ───────────────────────────────────────────────────────────

    async def get_public(self) -> ResumePublic:
        """Return the full resume for the public endpoint."""
        profile = await self._repo.get_profile()
        experience = await self._repo.list_experience()
        skill_groups = await self._repo.list_skill_groups()
        education = await self._repo.list_education()
        certifications = await self._repo.list_certifications()

        return ResumePublic(
            profile=ResumeProfilePublic.model_validate(profile),
            experience=[ResumeExperiencePublic.model_validate(e) for e in experience],
            skill_groups=[ResumeSkillGroupPublic.model_validate(g) for g in skill_groups],
            education=[ResumeEducationPublic.model_validate(e) for e in education],
            certifications=[ResumeCertificationPublic.model_validate(c) for c in certifications],
        )

    # ── Admin read ────────────────────────────────────────────────────────────

    async def get_admin(self) -> AdminResumeOut:
        """Return the full resume for the admin panel."""
        profile = await self._repo.get_profile()
        experience = await self._repo.list_experience()
        skill_groups = await self._repo.list_skill_groups()
        education = await self._repo.list_education()
        certifications = await self._repo.list_certifications()

        return AdminResumeOut(
            profile=AdminResumeProfileOut.model_validate(profile),
            experience=[AdminResumeExperienceOut.model_validate(e) for e in experience],
            skill_groups=[AdminResumeSkillGroupOut.model_validate(g) for g in skill_groups],
            education=[AdminResumeEducationOut.model_validate(e) for e in education],
            certifications=[AdminResumeCertificationOut.model_validate(c) for c in certifications],
        )

    # ── Profile mutations ─────────────────────────────────────────────────────

    async def update_profile(
        self,
        payload: ResumeProfileUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeProfileOut:
        row = await self._repo.update_profile(
            headline=payload.headline,
            summary_paragraphs=payload.summary_paragraphs,
            pdf_url=payload.pdf_url,
        )
        await self._audit.write(
            action="admin.resume.profile.updated",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id="profile",
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeProfileOut.model_validate(row)

    # ── Experience mutations ───────────────────────────────────────────────────

    async def create_experience(
        self,
        payload: ResumeExperienceCreate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeExperienceOut:
        row = await self._repo.create_experience(
            role=payload.role,
            context=payload.context,
            period=payload.period,
            highlights=payload.highlights,
        )
        await self._audit.write(
            action="admin.resume.experience.created",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(row.id),
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeExperienceOut.model_validate(row)

    async def update_experience(
        self,
        id: uuid.UUID,
        payload: ResumeExperienceUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeExperienceOut:
        row = await self._repo.get_experience(id)
        if row is None:
            raise LookupError(f"Experience entry {id} not found")
        row = await self._repo.update_experience(
            row,
            role=payload.role,
            context=payload.context,
            period=payload.period,
            highlights=payload.highlights,
        )
        await self._audit.write(
            action="admin.resume.experience.updated",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(id),
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeExperienceOut.model_validate(row)

    async def delete_experience(
        self,
        id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> None:
        row = await self._repo.get_experience(id)
        if row is None:
            raise LookupError(f"Experience entry {id} not found")
        await self._repo.delete_experience(row)
        await self._audit.write(
            action="admin.resume.experience.deleted",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(id),
            ip_address=ip_address,
        )
        await self._session.commit()

    # ── Skill group mutations ─────────────────────────────────────────────────

    async def create_skill_group(
        self,
        payload: ResumeSkillGroupCreate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeSkillGroupOut:
        row = await self._repo.create_skill_group(
            group_name=payload.group_name,
            skills=payload.skills,
        )
        await self._audit.write(
            action="admin.resume.skill_group.created",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(row.id),
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeSkillGroupOut.model_validate(row)

    async def update_skill_group(
        self,
        id: uuid.UUID,
        payload: ResumeSkillGroupUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeSkillGroupOut:
        row = await self._repo.get_skill_group(id)
        if row is None:
            raise LookupError(f"Skill group {id} not found")
        row = await self._repo.update_skill_group(
            row,
            group_name=payload.group_name,
            skills=payload.skills,
        )
        await self._audit.write(
            action="admin.resume.skill_group.updated",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(id),
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeSkillGroupOut.model_validate(row)

    async def delete_skill_group(
        self,
        id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> None:
        row = await self._repo.get_skill_group(id)
        if row is None:
            raise LookupError(f"Skill group {id} not found")
        await self._repo.delete_skill_group(row)
        await self._audit.write(
            action="admin.resume.skill_group.deleted",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(id),
            ip_address=ip_address,
        )
        await self._session.commit()

    # ── Education mutations ───────────────────────────────────────────────────

    async def create_education(
        self,
        payload: ResumeEducationCreate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeEducationOut:
        row = await self._repo.create_education(
            institution=payload.institution,
            degree=payload.degree,
            status=payload.status,
            notes=payload.notes,
        )
        await self._audit.write(
            action="admin.resume.education.created",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(row.id),
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeEducationOut.model_validate(row)

    async def update_education(
        self,
        id: uuid.UUID,
        payload: ResumeEducationUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeEducationOut:
        row = await self._repo.get_education(id)
        if row is None:
            raise LookupError(f"Education entry {id} not found")
        row = await self._repo.update_education(
            row,
            institution=payload.institution,
            degree=payload.degree,
            status=payload.status,
            notes=payload.notes,
        )
        await self._audit.write(
            action="admin.resume.education.updated",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(id),
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeEducationOut.model_validate(row)

    async def delete_education(
        self,
        id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> None:
        row = await self._repo.get_education(id)
        if row is None:
            raise LookupError(f"Education entry {id} not found")
        await self._repo.delete_education(row)
        await self._audit.write(
            action="admin.resume.education.deleted",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(id),
            ip_address=ip_address,
        )
        await self._session.commit()

    # ── Certification mutations ───────────────────────────────────────────────

    async def create_certification(
        self,
        payload: ResumeCertificationCreate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeCertificationOut:
        row = await self._repo.create_certification(
            title=payload.title,
            provider=payload.provider,
            status=payload.status,
        )
        await self._audit.write(
            action="admin.resume.certification.created",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(row.id),
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeCertificationOut.model_validate(row)

    async def update_certification(
        self,
        id: uuid.UUID,
        payload: ResumeCertificationUpdate,
        *,
        actor: str,
        ip_address: str | None,
    ) -> AdminResumeCertificationOut:
        row = await self._repo.get_certification(id)
        if row is None:
            raise LookupError(f"Certification {id} not found")
        row = await self._repo.update_certification(
            row,
            title=payload.title,
            provider=payload.provider,
            status=payload.status,
        )
        await self._audit.write(
            action="admin.resume.certification.updated",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(id),
            ip_address=ip_address,
        )
        await self._session.commit()
        return AdminResumeCertificationOut.model_validate(row)

    async def delete_certification(
        self,
        id: uuid.UUID,
        *,
        actor: str,
        ip_address: str | None,
    ) -> None:
        row = await self._repo.get_certification(id)
        if row is None:
            raise LookupError(f"Certification {id} not found")
        await self._repo.delete_certification(row)
        await self._audit.write(
            action="admin.resume.certification.deleted",
            actor=actor,
            resource_type=_RESOURCE,
            resource_id=str(id),
            ip_address=ip_address,
        )
        await self._session.commit()
