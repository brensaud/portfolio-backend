"""
Shared pytest fixtures for the backend test suite.

Database strategy:
  • Uses SQLite + aiosqlite (in-memory, per-test) — no PostgreSQL required.
  • A fresh SQLite database is created for each test function, guaranteeing
    complete test isolation.

Redis strategy:
  • Redis is intentionally not mocked — the lifespan gracefully degrades
    when Redis is unavailable, so rate limiting is simply skipped in tests.
  • To test rate limit enforcement, start a local Redis instance and run the
    integration test suite with ENVIRONMENT=test.

HTTP client:
  • httpx.AsyncClient with ASGITransport calls the full ASGI app, including
    middleware, exception handlers, and dependency injection.
"""

from __future__ import annotations

import os

# Set DATABASE_URL before any app module is imported so the module-level
# create_async_engine() in app.db.base uses SQLite instead of PostgreSQL.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# ── Per-test SQLite engine ────────────────────────────────────────────────────


@pytest.fixture
async def test_engine():
    """Create a fresh in-memory SQLite database for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session bound to the test SQLite database."""
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


# ── HTTP client with dependency overrides ────────────────────────────────────


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    AsyncClient wired to the FastAPI app with the test database injected.

    The real `get_db` dependency is overridden so all requests use the
    in-memory SQLite database instead of PostgreSQL.
    """

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
