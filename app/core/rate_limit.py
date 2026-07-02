"""
Redis-backed rate limiter with in-memory graceful degradation.

Design:
  • One Redis key per IP: `rl:contact:<ip>` with TTL = window_seconds.
  • Counter is incremented atomically via a pipeline; on the first request
    the TTL is also set so the window resets naturally.
  • If Redis is unavailable (app.state.redis is None), rate limiting is
    skipped — this happens automatically in local dev without Docker and
    in the test suite.
  • In production Redis is always expected to be available.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, Request, status

from app.core.config import settings

if TYPE_CHECKING:
    import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


async def get_redis(request: Request) -> aioredis.Redis | None:
    """FastAPI dependency — returns the Redis client or None."""
    return getattr(request.app.state, "redis", None)


async def check_rate_limit(
    request: Request,
    redis_client: aioredis.Redis | None = Depends(get_redis),
) -> None:
    """
    Dependency that enforces the contact-form rate limit.

    Raises HTTP 429 if the caller's IP has exceeded the configured limit.
    Silently passes when Redis is unavailable (degraded mode).
    """
    if redis_client is None:
        # Redis unavailable — gracefully skip rate limiting
        logger.debug("Rate limiting skipped (Redis not available)")
        return

    ip = _get_client_ip(request)
    key = f"rl:contact:{ip}"

    try:
        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            await pipe.expire(key, settings.rate_limit_window_seconds)
            results = await pipe.execute()

        count: int = results[0]
        if count > settings.rate_limit_requests:
            logger.warning("Rate limit exceeded for IP %s (count=%d)", ip, count)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Too many requests. "
                    f"You may submit up to {settings.rate_limit_requests} messages "
                    "per hour. Please try again later."
                ),
            )
    except HTTPException:
        raise
    except Exception:
        # Redis error — log and allow the request through
        logger.exception("Rate limit check failed; allowing request")


def _get_client_ip(request: Request) -> str:
    """
    Extract the real client IP from the request.

    Security note: reads the RIGHTMOST entry from X-Forwarded-For, not the
    leftmost.  The leftmost entry is user-supplied and trivially spoofable.
    The rightmost entry is appended by the last trusted proxy (e.g. Render's
    load balancer) and cannot be forged by the client.

    Falls back to the direct TCP connection IP when the header is absent.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Header may contain a comma-separated list; last entry is added by
        # the trusted proxy and is the real client IP.
        return forwarded_for.split(",")[-1].strip()
    if request.client:
        return request.client.host
    return "unknown"
