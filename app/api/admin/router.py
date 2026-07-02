"""
Admin API router.

Structure:
  /admin/api/auth/*   — authentication endpoints (no auth dependency here;
                        individual auth endpoints manage their own auth)

Future protected endpoints (e.g. contacts, analytics) should be registered
with the `_protected` prefix router so the get_current_admin dependency is
applied at the router level:

    _protected = APIRouter(dependencies=[Depends(get_current_admin)])
    admin_router.include_router(_protected_router, prefix="/contacts")
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.admin.auth import router as auth_router

admin_router = APIRouter(tags=["admin"])

# Auth sub-router — no auth dependency (handles its own cookie verification)
admin_router.include_router(auth_router, prefix="/auth")
