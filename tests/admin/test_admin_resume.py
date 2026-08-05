"""Tests for admin resume endpoints — /admin/api/resume."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import (
    ResumeExperience,
    ResumeProfile,
    ResumeSkillGroup,
    ResumeEducation,
    ResumeCertification,
)
from tests.admin.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD

BASE = "/admin/api/resume"


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _login(client: AsyncClient) -> None:
    resp = await client.post(
        "/admin/api/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"


async def _seed_profile(db: AsyncSession) -> ResumeProfile:
    row = ResumeProfile(
        id=1,
        headline="Test headline",
        summary_paragraphs=["Para 1", "Para 2"],
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def _seed_experience(db: AsyncSession) -> ResumeExperience:
    row = ResumeExperience(
        role="Backend Engineer",
        context="Independent",
        period="2024 – present",
        highlights=["Built things"],
        sort_order=0,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def _seed_skill_group(db: AsyncSession) -> ResumeSkillGroup:
    row = ResumeSkillGroup(
        group_name="Backend",
        skills=["Python", "FastAPI"],
        sort_order=0,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def _seed_education(db: AsyncSession) -> ResumeEducation:
    row = ResumeEducation(
        institution="Self-directed",
        degree="Software Engineering",
        status="In progress",
        notes=None,
        sort_order=0,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def _seed_certification(db: AsyncSession) -> ResumeCertification:
    row = ResumeCertification(
        title="AWS Cloud Practitioner",
        provider="AWS Training",
        status="Planned",
        sort_order=0,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


# ── Auth guard ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_resume_requires_auth(admin_client: AsyncClient) -> None:
    resp = await admin_client.get(BASE)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_requires_auth(admin_client: AsyncClient) -> None:
    resp = await admin_client.put(
        f"{BASE}/profile",
        json={"headline": "h", "summary_paragraphs": [], "pdf_url": None},
    )
    assert resp.status_code == 401


# ── GET /admin/api/resume ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_resume_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed_profile(db_session)
    await _login(admin_client)

    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    body = resp.json()
    assert "profile" in body
    assert "experience" in body
    assert "skill_groups" in body
    assert "education" in body
    assert "certifications" in body
    assert body["profile"]["headline"] == "Test headline"
    assert body["profile"]["summary_paragraphs"] == ["Para 1", "Para 2"]


@pytest.mark.asyncio
async def test_get_resume_creates_default_profile_if_absent(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    """Service creates the singleton profile row automatically."""
    await _login(admin_client)
    resp = await admin_client.get(BASE)
    assert resp.status_code == 200
    body = resp.json()
    assert body["profile"]["headline"] != ""


# ── PUT /admin/api/resume/profile ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_profile_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed_profile(db_session)
    await _login(admin_client)

    payload = {
        "headline": "New headline",
        "summary_paragraphs": ["Updated para"],
        "pdf_url": "/resume.pdf",
    }
    resp = await admin_client.put(f"{BASE}/profile", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["headline"] == "New headline"
    assert body["summary_paragraphs"] == ["Updated para"]
    assert body["pdf_url"] == "/resume.pdf"


@pytest.mark.asyncio
async def test_update_profile_rejects_empty_headline(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    await _seed_profile(db_session)
    await _login(admin_client)

    resp = await admin_client.put(
        f"{BASE}/profile",
        json={"headline": "", "summary_paragraphs": [], "pdf_url": None},
    )
    assert resp.status_code == 422


# ── POST /admin/api/resume/experience ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_experience_returns_201(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    payload = {
        "role": "Software Engineer",
        "context": "Company X",
        "period": "2023 – 2024",
        "highlights": ["Built API", "Led migrations"],
    }
    resp = await admin_client.post(f"{BASE}/experience", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "Software Engineer"
    assert body["highlights"] == ["Built API", "Led migrations"]
    assert "id" in body


@pytest.mark.asyncio
async def test_create_experience_missing_role_returns_422(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.post(
        f"{BASE}/experience",
        json={"context": "X", "period": "2024", "highlights": []},
    )
    assert resp.status_code == 422


# ── PUT /admin/api/resume/experience/{id} ─────────────────────────────────────


@pytest.mark.asyncio
async def test_update_experience_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    exp = await _seed_experience(db_session)
    await _login(admin_client)

    resp = await admin_client.put(
        f"{BASE}/experience/{exp.id}",
        json={
            "role": "Senior Engineer",
            "context": "Company Y",
            "period": "2025 – present",
            "highlights": ["New highlight"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "Senior Engineer"
    assert body["period"] == "2025 – present"


@pytest.mark.asyncio
async def test_update_experience_not_found(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.put(
        f"{BASE}/experience/{uuid.uuid4()}",
        json={"role": "X", "context": "Y", "period": "Z", "highlights": []},
    )
    assert resp.status_code == 404


# ── DELETE /admin/api/resume/experience/{id} ──────────────────────────────────


@pytest.mark.asyncio
async def test_delete_experience_returns_204(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    exp = await _seed_experience(db_session)
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/experience/{exp.id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_experience_not_found(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/experience/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── POST /admin/api/resume/skills ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_skill_group_returns_201(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.post(
        f"{BASE}/skills",
        json={"group_name": "DevOps", "skills": ["Docker", "GitHub Actions"]},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["group_name"] == "DevOps"
    assert "Docker" in body["skills"]


# ── PUT /admin/api/resume/skills/{id} ────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_skill_group_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    grp = await _seed_skill_group(db_session)
    await _login(admin_client)

    resp = await admin_client.put(
        f"{BASE}/skills/{grp.id}",
        json={"group_name": "Updated Group", "skills": ["Skill A"]},
    )
    assert resp.status_code == 200
    assert resp.json()["group_name"] == "Updated Group"


@pytest.mark.asyncio
async def test_update_skill_group_not_found(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.put(
        f"{BASE}/skills/{uuid.uuid4()}",
        json={"group_name": "X", "skills": []},
    )
    assert resp.status_code == 404


# ── DELETE /admin/api/resume/skills/{id} ─────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_skill_group_returns_204(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    grp = await _seed_skill_group(db_session)
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/skills/{grp.id}")
    assert resp.status_code == 204


# ── POST /admin/api/resume/education ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_education_returns_201(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.post(
        f"{BASE}/education",
        json={
            "institution": "MIT",
            "degree": "Computer Science",
            "status": "Completed",
            "notes": None,
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["institution"] == "MIT"
    assert body["status"] == "Completed"


@pytest.mark.asyncio
async def test_create_education_invalid_status(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.post(
        f"{BASE}/education",
        json={"institution": "X", "degree": "Y", "status": "Unknown", "notes": None},
    )
    assert resp.status_code == 422


# ── PUT /admin/api/resume/education/{id} ─────────────────────────────────────


@pytest.mark.asyncio
async def test_update_education_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    edu = await _seed_education(db_session)
    await _login(admin_client)

    resp = await admin_client.put(
        f"{BASE}/education/{edu.id}",
        json={"institution": "Oxford", "degree": "Philosophy", "status": "Planned", "notes": "One day"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["institution"] == "Oxford"
    assert body["status"] == "Planned"


@pytest.mark.asyncio
async def test_delete_education_returns_204(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    edu = await _seed_education(db_session)
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/education/{edu.id}")
    assert resp.status_code == 204


# ── POST /admin/api/resume/certifications ────────────────────────────────────


@pytest.mark.asyncio
async def test_create_certification_returns_201(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.post(
        f"{BASE}/certifications",
        json={"title": "AWS SAA", "provider": "AWS", "status": "In progress"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "AWS SAA"
    assert body["status"] == "In progress"


# ── PUT /admin/api/resume/certifications/{id} ────────────────────────────────


@pytest.mark.asyncio
async def test_update_certification_returns_200(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    cert = await _seed_certification(db_session)
    await _login(admin_client)

    resp = await admin_client.put(
        f"{BASE}/certifications/{cert.id}",
        json={"title": "AWS Solutions Architect", "provider": "AWS", "status": "Completed"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "Completed"


@pytest.mark.asyncio
async def test_delete_certification_returns_204(
    admin_client: AsyncClient, db_session: AsyncSession, admin_settings: None
) -> None:
    cert = await _seed_certification(db_session)
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/certifications/{cert.id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_certification_not_found(
    admin_client: AsyncClient, admin_settings: None
) -> None:
    await _login(admin_client)
    resp = await admin_client.delete(f"{BASE}/certifications/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── Public endpoint ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_public_resume_returns_200(admin_client: AsyncClient) -> None:
    """Public endpoint needs no auth."""
    resp = await admin_client.get("/api/v1/resume")
    assert resp.status_code == 200
    body = resp.json()
    assert "profile" in body
    assert "experience" in body
    assert "skill_groups" in body
    assert "education" in body
    assert "certifications" in body
