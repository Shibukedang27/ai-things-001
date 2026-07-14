from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.exceptions.handlers import register_exception_handlers
from backend.logging.config import configure_logging
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.middleware.request_id import RequestIDMiddleware
from backend.middleware.security_headers import SecurityHeadersMiddleware
from backend.routers.api import api_router
from backend.routers.health import router as health_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="ResearchForge OS backend API foundation.",
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        contact={
            "name": "ResearchForge OS",
            "url": "https://github.com/researchforge-os",
        },
        license_info={"name": "MIT"},
    )

    register_exception_handlers(app)

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        SecurityHeadersMiddleware,
        hsts_seconds=settings.security_hsts_seconds,
        enabled_hsts=settings.is_production,
    )
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_window=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
        excluded_path_prefixes=("/health", f"{settings.api_v1_prefix}/health", settings.openapi_url),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app
