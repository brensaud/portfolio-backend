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
    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,   # validates connections before use
        pool_size=5,
        max_overflow=10,
    )


engine: AsyncEngine = create_engine()
