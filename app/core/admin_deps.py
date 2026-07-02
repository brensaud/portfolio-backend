"""
Admin authentication FastAPI dependency.

`get_current_admin` is applied at the router level in app/api/admin/router.py
so every admin endpoint (except the auth sub-router) automatically requires a
valid access token cookie.

Usage in endpoint:
    async def my_endpoint(admin: str = Depends(get_current_admin)) -> ...:
        # `admin` is the admin email string from the JWT sub claim
        ...
"""

from __future__ import annotations

import logging

import jwt
from fastapi import HTTPException, Request, status

from app.core.admin_auth import decode_access_token

logger = logging.getLogger(__name__)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required.",
    headers={"WWW-Authenticate": "Cookie"},
)


async def get_current_admin(request: Request) -> str:
    """
    FastAPI dependency that validates the admin access token cookie.

    Returns the admin email (JWT sub claim) on success.
    Raises HTTP 401 if the cookie is missing, expired, or tampered.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise _UNAUTHORIZED

    try:
        email = decode_access_token(token)
    except jwt.InvalidTokenError:
        # Covers ExpiredSignatureError, DecodeError, InvalidAudienceError, etc.
        # Log at DEBUG — not WARNING — to avoid filling logs with automated probes.
        logger.debug("Admin access token validation failed")
        raise _UNAUTHORIZED

    return email
