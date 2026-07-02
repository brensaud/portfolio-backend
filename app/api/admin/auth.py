"""
Admin authentication endpoints.

Endpoint summary:
  POST   /admin/api/auth/login        — issue access + refresh token cookies
  POST   /admin/api/auth/logout       — revoke current session, clear cookies
  POST   /admin/api/auth/refresh      — rotate token pair (refresh-token rotation)
  GET    /admin/api/auth/me           — identity of authenticated admin
  GET    /admin/api/auth/sessions     — count of active sessions
  DELETE /admin/api/auth/sessions     — revoke ALL sessions
  PATCH  /admin/api/auth/password     — change admin password, revoke all sessions

Rate limiting strategy (login only):
  • Tier 1: 5 attempts per IP per 15 min → HTTP 429 with Retry-After header.
  • Tier 2: After 10 cumulative failures → 30-min IP lockout → HTTP 429.
  Both tiers degrade gracefully when Redis is unavailable (limiting is skipped).

Security notes:
  • bcrypt always runs on login regardless of whether the submitted email
    matches — see get_dummy_hash() in admin_auth for the timing attack detail.
  • All 401 responses share the same body to prevent user enumeration.
  • Redis GETDEL is atomic; an attacker cannot reuse a refresh token even under
    concurrent requests.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.admin_auth import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    get_dummy_hash,
    hash_refresh_token,
    set_access_token_cookie,
    set_refresh_token_cookie,
    token_expires_at,
    verify_password,
    hash_password,
)
from app.core.admin_deps import get_current_admin
from app.core.config import settings
from app.db.session import get_db
from app.repositories.audit_repo import AuditRepository
from app.schemas.admin.auth import (
    LoginRequest,
    LoginResponse,
    MeResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    RefreshResponse,
    SessionsResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Redis key templates
_RT_KEY = "admin:rt:{hash}"         # refresh token hash → admin email
_RT_ACTIVE_SET = "admin:rt:active"  # SSET of all active token hashes
_RL_KEY = "admin:rl:{ip}"           # rate-limit counter per IP
_LOCK_KEY = "admin:lock:{ip}"       # lockout flag per IP

# ── Helpers ───────────────────────────────────────────────────────────────────

_INVALID_CREDS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials.",
)


def _redis(request: Request):  # type: ignore[return]
    """Return the Redis client from app state, or None if unavailable."""
    return getattr(request.app.state, "redis", None)


def _client_ip(request: Request) -> str:
    """
    Extract the real client IP (rightmost X-Forwarded-For entry).

    The rightmost entry is appended by the trusted reverse proxy (Render)
    and cannot be forged by the client.  Falls back to the direct TCP
    connection host when the header is absent.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    if request.client:
        return request.client.host
    return "unknown"


async def _check_login_rate_limit(request: Request) -> None:
    """
    Enforce admin login rate limits using Redis sliding counters.

    Tier 1: ≥ admin_login_rate_limit_attempts in window → 429.
    Tier 2: ≥ admin_login_lockout_threshold cumulative failures → lockout.

    Gracefully no-ops when Redis is unavailable.
    """
    redis = _redis(request)
    if redis is None:
        return

    ip = _client_ip(request)
    lock_key = _LOCK_KEY.format(ip=ip)
    rl_key = _RL_KEY.format(ip=ip)

    try:
        # Tier 2: check active lockout first
        locked = await redis.get(lock_key)
        if locked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Please try again later.",
                headers={"Retry-After": str(settings.admin_login_lockout_seconds)},
            )

        # Tier 1: check sliding window counter
        count_raw = await redis.get(rl_key)
        count = int(count_raw) if count_raw else 0
        if count >= settings.admin_login_rate_limit_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
                headers={
                    "Retry-After": str(settings.admin_login_rate_limit_window_seconds)
                },
            )
    except HTTPException:
        raise
    except Exception:
        # Redis error — degrade gracefully, do not block the request.
        logger.warning("Admin login rate limit check failed; degrading gracefully")


async def _record_login_failure(request: Request) -> None:
    """
    Increment the per-IP failure counter after a failed login attempt.

    Escalates to a lockout once the cumulative threshold is reached.
    Gracefully no-ops when Redis is unavailable.
    """
    redis = _redis(request)
    if redis is None:
        return

    ip = _client_ip(request)
    rl_key = _RL_KEY.format(ip=ip)
    lock_key = _LOCK_KEY.format(ip=ip)

    try:
        # Increment and set expiry in one go
        count = await redis.incr(rl_key)
        await redis.expire(rl_key, settings.admin_login_rate_limit_window_seconds)

        # Escalate to lockout if cumulative failures exceed threshold
        if count >= settings.admin_login_lockout_threshold:
            await redis.set(lock_key, "1", ex=settings.admin_login_lockout_seconds)
    except Exception:
        logger.warning("Failed to record admin login failure in Redis")


async def _issue_token_pair(
    response: Response,
    email: str,
    redis,  # redis client or None
) -> datetime:
    """
    Create access + refresh tokens and attach them as cookies.

    Stores the refresh token hash in Redis when available.
    Returns the access token expiry timestamp.
    """
    access_token = create_access_token(email)
    refresh_token = create_refresh_token()
    rt_hash = hash_refresh_token(refresh_token)
    expires_at = token_expires_at()

    set_access_token_cookie(response, access_token)
    set_refresh_token_cookie(response, refresh_token)

    if redis is not None:
        try:
            rt_key = _RT_KEY.format(hash=rt_hash)
            await redis.set(rt_key, email, ex=settings.admin_refresh_ttl_seconds)
            await redis.sadd(_RT_ACTIVE_SET, rt_hash)
        except Exception:
            logger.warning("Failed to store refresh token in Redis; session won't be refreshable")

    return expires_at


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db=Depends(get_db),
) -> LoginResponse:
    """
    Authenticate the admin and issue access + refresh token cookies.

    Always runs bcrypt regardless of email match (timing attack prevention).
    Returns HTTP 401 with an identical body on any credential failure.
    """
    await _check_login_rate_limit(request)

    # Compute once — used for rate limiting, audit log, and request logging.
    client_ip = _client_ip(request)

    email_matches = body.email.lower() == settings.admin_email.lower()

    # Always run bcrypt — timing must be identical for wrong-email and
    # wrong-password paths.
    # If admin_password_hash is empty (unconfigured admin), compare against
    # the dummy hash so bcrypt still runs instead of short-circuiting.
    stored_hash = settings.admin_password_hash or get_dummy_hash()
    candidate_hash = stored_hash if email_matches else get_dummy_hash()
    password_ok = verify_password(body.password, candidate_hash)

    if not password_ok or not email_matches:
        await _record_login_failure(request)
        async with db as session:
            await AuditRepository(session).write(
                action="admin.login_failure",
                actor=body.email,
                ip_address=client_ip,
            )
            await session.commit()
        raise _INVALID_CREDS

    # Successful authentication — clear rate-limit counter for this IP.
    redis = _redis(request)
    if redis is not None:
        try:
            await redis.delete(_RL_KEY.format(ip=client_ip))
        except Exception:
            pass

    expires_at = await _issue_token_pair(response, body.email, redis)

    async with db as session:
        await AuditRepository(session).write(
            action="admin.login_success",
            actor=body.email,
            ip_address=client_ip,
        )
        await session.commit()

    logger.info("Admin login: %s from %s", body.email, client_ip)
    return LoginResponse(email=body.email, expires_at=expires_at)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    admin: str = Depends(get_current_admin),
    db=Depends(get_db),
) -> None:
    """
    Revoke the current session and clear auth cookies.

    Removes the refresh token hash from Redis atomically via GETDEL.
    The access token remains valid until its 15-min TTL expires — this is
    acceptable given the short window.
    """
    refresh_token = request.cookies.get("refresh_token")
    redis = _redis(request)

    if redis is not None and refresh_token:
        try:
            rt_hash = hash_refresh_token(refresh_token)
            await redis.getdel(_RT_KEY.format(hash=rt_hash))
            await redis.srem(_RT_ACTIVE_SET, rt_hash)
        except Exception:
            logger.warning("Failed to remove refresh token from Redis during logout")

    clear_auth_cookies(response)

    async with db as session:
        audit = AuditRepository(session)
        ip = request.headers.get("X-Forwarded-For", "").split(",")[-1].strip() or (
            request.client.host if request.client else None
        )
        await audit.write(action="admin.logout", actor=admin, ip_address=ip)
        await session.commit()


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    request: Request,
    response: Response,
    db=Depends(get_db),
) -> RefreshResponse:
    """
    Rotate the token pair using the refresh token cookie.

    Implementation:
      1. Read the refresh token from the HTTPOnly cookie.
      2. GETDEL the token hash from Redis (atomic — prevents replay attacks).
      3. If found, issue a new access + refresh token pair.
      4. Write audit log entry.

    Returns HTTP 401 when Redis is unavailable (fails closed).
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )

    redis = _redis(request)
    if redis is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session refresh unavailable. Please log in again.",
        )

    rt_hash = hash_refresh_token(refresh_token)
    rt_key = _RT_KEY.format(hash=rt_hash)

    try:
        email = await redis.getdel(rt_key)
    except Exception:
        logger.warning("Redis error during token refresh")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable.",
        )

    if not email:
        # Token not found — already used, expired, or forged
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again.",
        )

    # Remove old hash from active set before issuing new token
    try:
        await redis.srem(_RT_ACTIVE_SET, rt_hash)
    except Exception:
        pass

    expires_at = await _issue_token_pair(response, email, redis)

    async with db as session:
        audit = AuditRepository(session)
        ip = request.headers.get("X-Forwarded-For", "").split(",")[-1].strip() or (
            request.client.host if request.client else None
        )
        await audit.write(action="admin.token_refresh", actor=email, ip_address=ip)
        await session.commit()

    return RefreshResponse(expires_at=expires_at)


@router.get("/me", response_model=MeResponse)
async def me(
    request: Request,
    admin: str = Depends(get_current_admin),
) -> MeResponse:
    """Return identity and token expiry for the currently authenticated admin."""
    token = request.cookies.get("access_token")
    # Re-decode to extract the exp claim.  The token is already validated by
    # get_current_admin, so this decode will not fail under normal conditions.
    try:
        payload = jwt.decode(
            token,
            settings.admin_jwt_secret,
            algorithms=["HS256"],
            issuer=settings.admin_jwt_issuer,
            audience=settings.admin_jwt_audience,
        )
        expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
    except Exception:
        # Fallback: estimate from current time (token is still valid or we
        # wouldn't have reached this point).
        expires_at = token_expires_at()

    return MeResponse(email=admin, expires_at=expires_at)


@router.get("/sessions", response_model=SessionsResponse)
async def sessions_count(
    request: Request,
    admin: str = Depends(get_current_admin),
) -> SessionsResponse:
    """Return the number of active refresh token sessions."""
    redis = _redis(request)
    if redis is None:
        return SessionsResponse(active_sessions=0)

    try:
        count = await redis.scard(_RT_ACTIVE_SET)
    except Exception:
        count = 0

    return SessionsResponse(active_sessions=count)


@router.delete("/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_all_sessions(
    request: Request,
    response: Response,
    admin: str = Depends(get_current_admin),
    db=Depends(get_db),
) -> None:
    """
    Revoke ALL active admin sessions.

    Removes every refresh token hash from Redis and clears the caller's
    cookies.  Access tokens remain valid until their 15-min TTL — acceptable
    for an emergency revocation.
    """
    redis = _redis(request)

    if redis is not None:
        try:
            hashes = await redis.smembers(_RT_ACTIVE_SET)
            if hashes:
                keys = [_RT_KEY.format(hash=h) for h in hashes]
                await redis.delete(*keys)
            await redis.delete(_RT_ACTIVE_SET)
        except Exception:
            logger.warning("Failed to revoke all sessions in Redis")

    clear_auth_cookies(response)

    async with db as session:
        audit = AuditRepository(session)
        ip = request.headers.get("X-Forwarded-For", "").split(",")[-1].strip() or (
            request.client.host if request.client else None
        )
        await audit.write(
            action="admin.sessions_revoked_all",
            actor=admin,
            ip_address=ip,
        )
        await session.commit()


@router.patch("/password", response_model=PasswordChangeResponse)
async def change_password(
    body: PasswordChangeRequest,
    request: Request,
    response: Response,
    admin: str = Depends(get_current_admin),
    db=Depends(get_db),
) -> PasswordChangeResponse:
    """
    Change the admin password.

    Verifies the current password, hashes the new one at cost 12, and
    revokes all sessions.  Returns the new bcrypt hash — the operator must
    update ADMIN_PASSWORD_HASH in the deployment environment.

    Note: because admin credentials are stored in env vars (not the DB),
    this endpoint cannot update the stored hash directly.  The returned
    hash must be set manually.
    """
    if not verify_password(body.current_password, settings.admin_password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect.",
        )

    new_hash = hash_password(body.new_password)

    # Revoke all existing sessions
    redis = _redis(request)
    if redis is not None:
        try:
            hashes = await redis.smembers(_RT_ACTIVE_SET)
            if hashes:
                keys = [_RT_KEY.format(hash=h) for h in hashes]
                await redis.delete(*keys)
            await redis.delete(_RT_ACTIVE_SET)
        except Exception:
            logger.warning("Failed to revoke sessions during password change")

    clear_auth_cookies(response)

    async with db as session:
        audit = AuditRepository(session)
        ip = request.headers.get("X-Forwarded-For", "").split(",")[-1].strip() or (
            request.client.host if request.client else None
        )
        await audit.write(action="admin.password_changed", actor=admin, ip_address=ip)
        await session.commit()

    return PasswordChangeResponse(new_password_hash=new_hash)
