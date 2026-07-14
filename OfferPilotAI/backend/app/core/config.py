"""Application configuration and environment variable mapping."""

from enum import StrEnum
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Runtime environment values."""

    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class LogFormat(StrEnum):
    """Supported log output formats."""

    CONSOLE = "console"
    JSON = "json"


class Settings(BaseSettings):
    """Typed settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="OFFERPILOT_AI_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "OfferPilot AI API"
    app_version: str = "0.1.0"
    environment: Environment = Environment.LOCAL
    debug: bool = False

    api_v1_prefix: str = "/api/v1"
    docs_enabled: bool = True

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = Field(
        default="postgresql+asyncpg://offerpilotai:offerpilotai_change_me@localhost:5432/offerpilotai"
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"])

    trusted_hosts: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1", "testserver", "*.localhost"])

    auth_enabled: bool = False
    api_key: str | None = None
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    password_reset_token_expire_minutes: int = 30
    max_login_attempts: int = 5
    account_lock_minutes: int = 15

    live_code_execution_enabled: bool = True
    live_code_default_timeout_seconds: float = 3.0
    live_code_max_timeout_seconds: float = 8.0
    live_code_max_source_chars: int = 50_000
    live_code_max_stdin_chars: int = 20_000

    resume_pdf_max_bytes: int = 5_000_000
    resume_text_max_chars: int = 120_000

    request_id_header: str = "X-Request-ID"
    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.JSON

    readiness_database_check_enabled: bool = True

    @field_validator("cors_origins", "cors_allow_methods", "cors_allow_headers", "trusted_hosts", mode="before")
    @classmethod
    def parse_csv_or_list(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("docs_enabled")
    @classmethod
    def disable_docs_in_production_when_debug_false(cls, value: bool, info) -> bool:
        environment = info.data.get("environment")
        debug = info.data.get("debug")
        if environment == Environment.PRODUCTION and not debug:
            return False
        return value

    @model_validator(mode="after")
    def require_secure_production_secrets(self) -> "Settings":
        if self.environment == Environment.PRODUCTION and self.jwt_secret_key == "change-me-in-production":
            raise ValueError("OFFERPILOT_AI_JWT_SECRET_KEY must be configured in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()
