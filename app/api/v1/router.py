"""v1 API router — aggregates all v1 endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import analytics, articles, availability, case_studies, contact, health, projects, resume, settings

router = APIRouter()

router.include_router(health.router)
router.include_router(contact.router)
router.include_router(articles.router)
router.include_router(projects.router)
router.include_router(availability.router)
router.include_router(settings.router)
router.include_router(resume.router)
router.include_router(case_studies.router)
router.include_router(analytics.router)
