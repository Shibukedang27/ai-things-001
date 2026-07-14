from typing import Literal

from backend.schemas.common import APIModel


class ServiceHealth(APIModel):
    name: str
    status: Literal["ok", "degraded", "down"]
    latency_ms: float | None = None
    detail: str | None = None


class HealthResponse(APIModel):
    status: Literal["ok", "degraded", "down"]
    version: str
    environment: str
    services: list[ServiceHealth]
