"""v1 API router — aggregates all v1 endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import articles, contact, health

router = APIRouter()

router.include_router(health.router)
router.include_router(contact.router)
router.include_router(articles.router)
router.include_router(articles.router)
