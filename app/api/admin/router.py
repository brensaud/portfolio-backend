"""
Admin API router.

Structure:
  /admin/api/auth/*                — authentication (no blanket auth dependency;
                                     individual auth endpoints manage their own)
  /admin/api/contact-messages/*   — contact message management (protected)

Protected sub-routers are assembled with get_current_admin applied at the
router level so every child endpoint is automatically authenticated without
any per-endpoint boilerplate.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.admin.auth import router as auth_router
from app.api.admin.contact_messages import router as contact_messages_router
from app.core.admin_deps import get_current_admin

admin_router = APIRouter(tags=["admin"])

# ── Public sub-router ─────────────────────────────────────────────────────────
# Auth endpoints handle their own cookie verification — no blanket dependency.
admin_router.include_router(auth_router, prefix="/auth")

# ── Protected sub-routers ─────────────────────────────────────────────────────
# get_current_admin is applied once here at the router level.  Every endpoint
# registered below is protected without needing to declare the dependency
# individually.
_protected = APIRouter(dependencies=[Depends(get_current_admin)])
_protected.include_router(
    contact_messages_router,
    prefix="/contact-messages",
    tags=["admin-contact-messages"],
)
admin_router.include_router(_protected)
