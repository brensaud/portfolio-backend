"""
Database session dependency for FastAPI.

Usage in route handlers:
    async def my_endpoint(db: AsyncSession = Depends(get_db)) -> ...:
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.base import engine

_async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,  # avoid lazy-load errors after commit
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session; close it when the request finishes."""
    async with _async_session_factory() as session:
        yield session
