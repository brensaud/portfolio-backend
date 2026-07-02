"""
Application settings — loaded from environment variables / .env file.

All configuration is centralised here.  Import `settings` everywhere;
never access `os.environ` directly in application code.
"""

from __future__ import annotations

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "Portfolio API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────────────────
    # asyncpg driver — required for async SQLAlchemy
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio"

    # ── Redis ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Accepts a JSON-encoded list in the environment:
    #   ALLOWED_ORIGINS='["http://localhost:5173","https://example.com"]'
    allowed_origins: list[str] = ["http://localhost:5173"]

    # ── Rate limiting ─────────────────────────────────────────────────────────
    rate_limit_requests: int = 5  # max submissions per IP per window
    rate_limit_window_seconds: int = 3600  # 1 hour

    # ── Admin authentication ──────────────────────────────────────────────────
    # Credentials live in environment variables — no admin_users DB table.
    # Generate ADMIN_PASSWORD_HASH with: python -m app.cli.hash_password
    #
    # Development defaults are intentionally obvious placeholders; they fail
    # the production validator so misconfigured deploys surface immediately.
    admin_email: str = ""
    admin_password_hash: str = ""
    # Must be ≥ 32 characters.  Generate with: python -c "import secrets; print(secrets.token_hex(64))"
    admin_jwt_secret: str = "dev-secret-CHANGE-IN-PRODUCTION-must-be-32-plus-chars!!"
    admin_jwt_issuer: str = "api.brensaud.com"
    admin_jwt_audience: str = "admin.brensaud.com"
    admin_jwt_access_ttl_minutes: int = 15
    admin_refresh_ttl_seconds: int = 86400  # 24 hours

    # Admin login rate limiting (per IP)
    admin_login_rate_limit_attempts: int = 5
    admin_login_rate_limit_window_seconds: int = 900  # 15 minutes
    # After this many cumulative failures, lock the IP for lockout_seconds
    admin_login_lockout_threshold: int = 10
    admin_login_lockout_seconds: int = 1800  # 30 minutes

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

    @model_validator(mode="after")
    def validate_production_requirements(self) -> "Settings":
        """Fail fast on misconfigured production deployments."""
        if not self.is_production:
            return self

        errors: list[str] = []

        # Admin credentials must be explicitly configured
        if not self.admin_email:
            errors.append("ADMIN_EMAIL must be set in production")
        if not self.admin_password_hash:
            errors.append("ADMIN_PASSWORD_HASH must be set in production")
        elif not self.admin_password_hash.startswith("$2b$"):
            errors.append("ADMIN_PASSWORD_HASH must be a valid bcrypt hash (starts with $2b$)")

        # JWT secret must be cryptographically strong
        if len(self.admin_jwt_secret) < 32:
            errors.append("ADMIN_JWT_SECRET must be at least 32 characters in production")

        # CORS origins must be explicit HTTPS URLs in production
        for origin in self.allowed_origins:
            if origin == "*" or not origin.startswith("https://"):
                errors.append(
                    f"ALLOWED_ORIGINS contains unsafe value in production: {origin!r}"
                )

        if errors:
            raise ValueError("Production configuration errors:\n" + "\n".join(f"  • {e}" for e in errors))

        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def admin_configured(self) -> bool:
        """True when admin credentials have been set (non-empty)."""
        return bool(self.admin_email and self.admin_password_hash)


settings = Settings()
