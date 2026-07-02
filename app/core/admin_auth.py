"""
Admin authentication utilities.

Responsibilities:
  • JWT access token creation and verification (HS256 via PyJWT).
  • Bcrypt password verification and hashing via passlib.
  • HTTPOnly cookie helpers (set / clear).
  • Refresh token generation and SHA-256 hashing for Redis storage.
  • Dummy hash for constant-time login comparison (timing attack prevention).

Security notes:
  • The dummy hash (_DUMMY_HASH) is computed once at import time.  It is
    compared against the submitted password whenever the admin email does NOT
    match, ensuring bcrypt always runs regardless of email validity and the
    response timing is indistinguishable between "wrong email" and "wrong
    password" scenarios.
  • Cookie Secure flag is True only in production.  In development and tests
    the flag is omitted so cookies work over plain HTTP (localhost).
  • Cookie SameSite=Strict: brensaud.com and api.brensaud.com share the same
    eTLD+1, so they are treated as same-site and the cookie is sent in all
    legitimate cross-subdomain admin API calls.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
import bcrypt
from fastapi import Response

from app.core.config import settings

# ── Password hashing ──────────────────────────────────────────────────────────

# bcrypt hard-limits input to 72 bytes; passwords longer than that are silently
# truncated (or rejected in bcrypt >= 5.0).  We SHA-256 prehash the password
# first: SHA-256 always produces 32 bytes, well within the limit, so passwords
# of any length are supported without truncation or errors.
#
# All hashes in this system are generated with the same prehash — the CLI tool
# and this module must stay consistent.

_BCRYPT_ROUNDS = 12


def _prehash(plain: str) -> bytes:
    """SHA-256 prehash a plaintext password before bcrypt."""
    return hashlib.sha256(plain.encode()).digest()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash (SHA-256 prehashed)."""
    return bcrypt.checkpw(_prehash(plain), hashed.encode())


def hash_password(plain: str) -> str:
    """Hash a plaintext password with SHA-256 prehash + bcrypt at cost 12."""
    return bcrypt.hashpw(_prehash(plain), bcrypt.gensalt(_BCRYPT_ROUNDS)).decode()


# Pre-computed dummy hash for constant-time comparison.
# Computed at module load (once).  Cost 12 matches production hashes so the
# timing for "wrong email" is indistinguishable from "wrong password".
_DUMMY_HASH: str = hash_password("dummy-constant-time-password-not-real-DO-NOT-USE")


def get_dummy_hash() -> str:
    """Return the pre-computed dummy hash for constant-time comparisons."""
    return _DUMMY_HASH


# ── JWT ───────────────────────────────────────────────────────────────────────


def create_access_token(email: str) -> str:
    """
    Issue a signed HS256 JWT access token for the admin.

    Claims: sub (email), iat, exp, iss, aud.
    """
    now = datetime.now(UTC)
    exp = now + timedelta(minutes=settings.admin_jwt_access_ttl_minutes)
    payload: dict[str, object] = {
        "sub": email,
        "jti": str(uuid.uuid4()),  # unique token ID — ensures each token is distinct
        "iat": now,
        "exp": exp,
        "iss": settings.admin_jwt_issuer,
        "aud": settings.admin_jwt_audience,
    }
    return jwt.encode(payload, settings.admin_jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> str:
    """
    Decode and validate a JWT access token.

    Returns the admin email (sub claim) on success.
    Raises jwt.InvalidTokenError (or a subclass) on any failure, including
    expiry, wrong issuer/audience, and tampered signature.
    """
    payload = jwt.decode(
        token,
        settings.admin_jwt_secret,
        algorithms=["HS256"],
        issuer=settings.admin_jwt_issuer,
        audience=settings.admin_jwt_audience,
    )
    sub: str = payload["sub"]
    return sub


def token_expires_at() -> datetime:
    """Return the expiry timestamp for the next access token."""
    return datetime.now(UTC) + timedelta(minutes=settings.admin_jwt_access_ttl_minutes)


# ── Refresh tokens ────────────────────────────────────────────────────────────


def create_refresh_token() -> str:
    """Generate a cryptographically random 32-byte (64 hex chars) refresh token."""
    return secrets.token_hex(32)


def hash_refresh_token(raw_token: str) -> str:
    """
    SHA-256 hash the raw refresh token for safe storage in Redis.

    Only the hash is stored; the raw token is only ever held in the
    HTTPOnly cookie on the client.
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()


# ── Cookie helpers ────────────────────────────────────────────────────────────

# The Secure flag is only set in production (HTTPS).  In local development and
# tests the app runs over plain HTTP, so Secure would silently drop the cookie.
def _secure() -> bool:
    return settings.is_production


def set_access_token_cookie(response: Response, token: str) -> None:
    """
    Attach the access token as an HTTPOnly cookie to the response.

    Path is scoped to /admin/api so the cookie is never sent on public
    API requests or on any other path.
    """
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=_secure(),
        samesite="strict",
        path="/admin/api",
        max_age=settings.admin_jwt_access_ttl_minutes * 60,
    )


def set_refresh_token_cookie(response: Response, token: str) -> None:
    """
    Attach the refresh token as an HTTPOnly cookie to the response.

    Path is scoped to /admin/api/auth/refresh — the tightest scope
    possible.  The browser will only send this cookie to that exact path.
    """
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=_secure(),
        samesite="strict",
        path="/admin/api/auth/refresh",
        max_age=settings.admin_refresh_ttl_seconds,
    )


def clear_auth_cookies(response: Response) -> None:
    """
    Clear both auth cookies by setting Max-Age=0.

    Path must exactly match the path used when the cookie was set, otherwise
    the browser keeps the old cookie.
    """
    response.delete_cookie(key="access_token", path="/admin/api", samesite="strict")
    response.delete_cookie(
        key="refresh_token", path="/admin/api/auth/refresh", samesite="strict"
    )
