"""
Admin authentication request and response schemas.

All schemas follow strict validation rules — extra fields are forbidden to
prevent parameter pollution and accidental PII leakage.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Request schemas ────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class PasswordChangeRequest(BaseModel):
    """Change the admin password.  Returns the new hash for manual env-var update."""

    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(min_length=1, max_length=1024)
    new_password: str = Field(
        min_length=12,
        max_length=1024,
        description="New password — minimum 12 characters.",
    )


# ── Response schemas ───────────────────────────────────────────────────────────


class LoginResponse(BaseModel):
    """Returned on successful login — safe to include in the response body."""

    email: str
    expires_at: datetime


class MeResponse(BaseModel):
    """Identity of the currently authenticated admin."""

    email: str
    expires_at: datetime


class RefreshResponse(BaseModel):
    """Returned when the access token is successfully rotated."""

    expires_at: datetime


class SessionsResponse(BaseModel):
    """Current active refresh-token session count."""

    active_sessions: int


class PasswordChangeResponse(BaseModel):
    """
    Returned after a successful password change.

    The new_password_hash must be copied into the ADMIN_PASSWORD_HASH
    environment variable.  The old sessions are revoked server-side.
    """

    new_password_hash: str
    instruction: str = (
        "Copy new_password_hash into your ADMIN_PASSWORD_HASH environment variable "
        "and redeploy.  All previous sessions have been revoked."
    )
