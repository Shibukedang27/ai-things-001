import time

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.config import Settings
from backend.schemas.health import HealthResponse, ServiceHealth


class HealthService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    def readiness(self) -> HealthResponse:
        database_health = self._database_health()
        status = "ok" if database_health.status == "ok" else "degraded"
        return HealthResponse(
            status=status,
            version=self.settings.app_version,
            environment=self.settings.environment,
            services=[database_health],
        )

    def liveness(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            version=self.settings.app_version,
            environment=self.settings.environment,
            services=[ServiceHealth(name="api", status="ok")],
        )

    def _database_health(self) -> ServiceHealth:
        start = time.perf_counter()
        try:
            self.session.execute(text("SELECT 1"))
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            return ServiceHealth(name="postgres", status="down", latency_ms=elapsed_ms, detail=str(exc))
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        return ServiceHealth(name="postgres", status="ok", latency_ms=elapsed_ms)
