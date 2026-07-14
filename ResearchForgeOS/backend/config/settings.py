from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ResearchForge OS API"
    app_version: str = "0.2.0"
    environment: Literal["local", "development", "staging", "production", "test"] = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://researchforge:researchforge_dev_password@localhost:5432/researchforge"
    database_pool_size: int = Field(default=10, ge=1, le=100)
    database_max_overflow: int = Field(default=20, ge=0, le=100)
    database_pool_timeout: int = Field(default=30, ge=1, le=120)

    jwt_secret_key: str = "change-this-development-secret-before-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    refresh_token_expire_days: int = Field(default=14, ge=1, le=90)
    password_hash_rounds: int = Field(default=12, ge=10, le=15)

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["Authorization", "Content-Type", "X-Request-ID"])

    rate_limit_requests: int = Field(default=120, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)

    security_hsts_seconds: int = Field(default=31536000, ge=0)
    log_level: str = "INFO"
    log_json: bool = True

    retrieval_namespace: str = "researchforge"
    retrieval_collection_name: str = "knowledge"
    retrieval_vector_backend: Literal["memory", "chroma"] = "memory"
    retrieval_chroma_persist_directory: str = ".chroma"
    retrieval_max_context_characters: int = Field(default=1200, ge=240, le=8000)

    @field_validator("cors_origins", "cors_allow_methods", "cors_allow_headers", mode="before")
    @classmethod
    def parse_csv_or_list(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("api_v1_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith("/"):
            value = f"/{value}"
        return value.rstrip("/")

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        unsafe_secret = "change-this-development-secret-before-production"
        if self.environment == "production" and self.jwt_secret_key == unsafe_secret:
            raise ValueError("jwt_secret_key must be configured for production")
        if self.environment == "production" and not self.database_url.startswith("postgresql"):
            raise ValueError("database_url must point to PostgreSQL in production")
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def docs_url(self) -> str | None:
        return None if self.is_production else f"{self.api_v1_prefix}/docs"

    @property
    def redoc_url(self) -> str | None:
        return None if self.is_production else f"{self.api_v1_prefix}/redoc"

    @property
    def openapi_url(self) -> str:
        return f"{self.api_v1_prefix}/openapi.json"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
