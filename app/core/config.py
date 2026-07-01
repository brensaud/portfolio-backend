"""
Application settings — loaded from environment variables / .env file.

All configuration is centralised here.  Import `settings` everywhere;
never access `os.environ` directly in application code.
"""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "Portfolio API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────────────────
    # asyncpg driver — required for async SQLAlchemy
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio"
    )

    # ── Redis ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Accepts a JSON-encoded list in the environment:
    #   ALLOWED_ORIGINS='["http://localhost:5173","https://example.com"]'
    allowed_origins: list[str] = ["http://localhost:5173"]

    # ── Rate limiting ─────────────────────────────────────────────────────────
    rate_limit_requests: int = 5        # max submissions per IP per window
    rate_limit_window_seconds: int = 3600  # 1 hour

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
