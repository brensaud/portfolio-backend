"""
Async SQLAlchemy engine and declarative base.

All ORM models inherit from `Base`.  The engine is created once at module
import time; connection pools are managed by SQLAlchemy.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(AsyncAttrs, DeclarativeBase):
    """Shared declarative base for all ORM models."""


def create_engine() -> AsyncEngine:
    url_str = str(settings.database_url)
    # SQLite's StaticPool rejects pool_size/max_overflow; omit them for sqlite URLs
    pool_kwargs = {} if "sqlite" in url_str else {"pool_size": 5, "max_overflow": 10}
    return create_async_engine(
        url_str,
        echo=settings.debug,
        pool_pre_ping=True,
        **pool_kwargs,
    )


engine: AsyncEngine = create_engine()
