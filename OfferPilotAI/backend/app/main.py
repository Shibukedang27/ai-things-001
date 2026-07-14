"""FastAPI application factory for OfferPilot AI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import register_middleware
from app.core.openapi import OPENAPI_TAGS
from app.schemas.common import APIResponse
from app.utils.time import utc_now

logger = get_logger(__name__)


def build_lifespan(settings: Settings):
    """Create an application lifespan handler bound to concrete settings."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logger.info(
            "application_starting",
            extra={
                "app_name": settings.app_name,
                "environment": settings.environment,
                "version": settings.app_version,
            },
        )
        yield
        logger.info("application_stopping")

    return lifespan


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        summary="Production-ready REST API foundation for OfferPilot AI.",
        description=(
            "OfferPilot AI backend API for AI-assisted interview preparation, "
            "practice sessions, question catalogs, scoring, and operational health."
        ),
        version=settings.app_version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        openapi_tags=OPENAPI_TAGS,
        lifespan=build_lifespan(settings),
    )

    app.state.settings = settings

    register_middleware(app, settings)
    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", response_model=APIResponse[dict[str, str]], include_in_schema=False)
    async def root() -> APIResponse[dict[str, str]]:
        return APIResponse(
            data={
                "service": settings.app_name,
                "version": settings.app_version,
                "docs": "/docs" if settings.docs_enabled else "disabled",
            },
            meta={"timestamp": utc_now().isoformat()},
        )

    return app


app = create_app()
