"""
Shared custom SQLAlchemy type descriptors.

StringArray — a list-of-strings column that uses PostgreSQL ARRAY(String)
in production and JSON in SQLite (test environment).  Defined once here so
all models can reuse it without circular imports.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import JSON, TypeDecorator


class StringArray(TypeDecorator[list[str]]):
    """List-of-strings: ARRAY(String) on PostgreSQL, JSON on SQLite."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        return dialect.type_descriptor(JSON)

    def process_bind_param(self, value: list[str] | None, dialect: Any) -> Any:  # type: ignore[override]
        if value is None:
            return []
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value: Any, dialect: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return []
        return list(value)
