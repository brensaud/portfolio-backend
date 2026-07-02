"""
Fixtures shared across all admin test modules.

Key design decisions:
  • TEST_ADMIN_HASH uses bcrypt cost 4 (generated once per session).
    Cost 4 verifies in ~1 ms instead of ~400 ms, keeping the suite fast while
    still exercising the real passlib bcrypt path.
  • admin_settings patches app.core.config.settings at attribute level so any
    code that reads settings.admin_email at call time (not import time) uses the
    test values.
  • FakeRedis is a minimal dict-backed async implementation covering the exact
    set of Redis operations used by the admin auth endpoints.
  • The admin_client fixture composes db_session + FakeRedis + settings patches
    in one place so individual tests stay concise.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import hashlib

import bcrypt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.main import app

# ── Test admin credentials ────────────────────────────────────────────────────

TEST_ADMIN_EMAIL = "admin@example.com"
TEST_ADMIN_PASSWORD = "correct-horse-battery-staple-admin"  # ≥ 12 chars
TEST_JWT_SECRET = "test-jwt-secret-32-characters-long!!"  # exactly 37 chars


# ── Session-scoped bcrypt hash (cost 4 for speed) ─────────────────────────────


@pytest.fixture(scope="session")
def test_admin_hash() -> str:
    """
    Pre-compute a bcrypt hash with cost 4 once per test session.

    Uses the same SHA-256 prehash as production (admin_auth._prehash).
    Cost 4 runs in ~1 ms instead of ~400 ms.  Do NOT use cost 4 outside tests.
    """
    prehashed = hashlib.sha256(TEST_ADMIN_PASSWORD.encode()).digest()
    return bcrypt.hashpw(prehashed, bcrypt.gensalt(rounds=4)).decode()


# ── Settings patch ────────────────────────────────────────────────────────────


@pytest.fixture
def admin_settings(monkeypatch, test_admin_hash: str) -> None:
    """
    Patch the global settings singleton with safe test admin credentials.

    Uses monkeypatch.setattr on the already-instantiated settings object so
    that code importing `from app.core.config import settings` picks up the
    patched values without module reloading.
    """
    import app.core.config as _cfg_module
    import app.core.admin_auth as _auth_module

    monkeypatch.setattr(_cfg_module.settings, "admin_email", TEST_ADMIN_EMAIL)
    monkeypatch.setattr(_cfg_module.settings, "admin_password_hash", test_admin_hash)
    monkeypatch.setattr(_cfg_module.settings, "admin_jwt_secret", TEST_JWT_SECRET)
    # Keep issuer/audience consistent so JWTs created during tests decode correctly
    monkeypatch.setattr(_cfg_module.settings, "admin_jwt_issuer", "api.test.local")
    monkeypatch.setattr(_cfg_module.settings, "admin_jwt_audience", "admin.test.local")
    monkeypatch.setattr(_cfg_module.settings, "admin_jwt_access_ttl_minutes", 15)


# ── FakeRedis ─────────────────────────────────────────────────────────────────


class FakeRedis:
    """
    Minimal async dict-backed Redis substitute for unit tests.

    Supports the exact operations used by admin auth endpoints:
      set, get, getdel, incr, expire, delete, sadd, srem, scard, smembers, ping.

    TTL is intentionally not enforced — tests do not rely on expiry timing.
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        self._store[key] = str(value)

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def getdel(self, key: str) -> str | None:
        return self._store.pop(key, None)

    async def incr(self, key: str) -> int:
        val = int(self._store.get(key, "0")) + 1
        self._store[key] = str(val)
        return val

    async def expire(self, key: str, seconds: int) -> None:
        # TTL not enforced in tests
        pass

    async def delete(self, *keys: str) -> None:
        for key in keys:
            self._store.pop(key, None)
            self._sets.pop(key, None)

    async def sadd(self, key: str, *values: str) -> None:
        self._sets.setdefault(key, set()).update(values)

    async def srem(self, key: str, *values: str) -> None:
        self._sets.get(key, set()).discard(*values)

    async def scard(self, key: str) -> int:
        return len(self._sets.get(key, set()))

    async def smembers(self, key: str) -> set[str]:
        return self._sets.get(key, set()).copy()

    async def ping(self) -> bool:
        return True


# ── Client fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
async def admin_client(
    db_session: AsyncSession,
    admin_settings,  # applies settings patches
) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP client wired to the app with test admin credentials, no Redis.

    Use this fixture when testing endpoints that do NOT require Redis
    (login without rate limiting, /me, /logout without refresh token checks).
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.state.redis = None  # No Redis — rate limiting and refresh skipped

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    app.state.redis = None


@pytest.fixture
async def admin_client_with_redis(
    db_session: AsyncSession,
    admin_settings,
) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP client wired to the app with test admin credentials AND FakeRedis.

    Use this fixture when testing refresh token rotation, session counting,
    or session revocation.
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    fake_redis = FakeRedis()
    app.state.redis = fake_redis

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    app.state.redis = None
