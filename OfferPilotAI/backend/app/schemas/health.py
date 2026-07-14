"""Health response schemas."""

from pydantic import BaseModel, Field


class DependencyStatus(BaseModel):
    """Dependency readiness state."""

    name: str
    healthy: bool
    details: str | None = None


class HealthStatus(BaseModel):
    """Application health state."""

    status: str = Field(..., examples=["healthy"])
    service: str
    version: str
    environment: str
    timestamp: str


class ReadinessStatus(HealthStatus):
    """Application readiness state."""

    ready: bool
    dependencies: list[DependencyStatus]
