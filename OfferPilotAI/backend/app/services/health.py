"""Health service."""

from app.core.config import Settings
from app.db.session import check_database_connection
from app.schemas.health import DependencyStatus, HealthStatus, ReadinessStatus
from app.utils.time import utc_now


class HealthService:
    """Build health and readiness responses."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_health(self) -> HealthStatus:
        return HealthStatus(
            status="healthy",
            service=self.settings.app_name,
            version=self.settings.app_version,
            environment=self.settings.environment,
            timestamp=utc_now().isoformat(),
        )

    async def get_readiness(self) -> ReadinessStatus:
        dependencies: list[DependencyStatus] = []

        if self.settings.readiness_database_check_enabled:
            database_healthy = await check_database_connection()
            dependencies.append(
                DependencyStatus(
                    name="database",
                    healthy=database_healthy,
                    details="reachable" if database_healthy else "unreachable",
                )
            )

        ready = all(dependency.healthy for dependency in dependencies)

        return ReadinessStatus(
            status="ready" if ready else "not_ready",
            service=self.settings.app_name,
            version=self.settings.app_version,
            environment=self.settings.environment,
            timestamp=utc_now().isoformat(),
            ready=ready,
            dependencies=dependencies,
        )
