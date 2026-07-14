"""Custom application exceptions and handlers."""

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.schemas.common import APIResponse, ErrorDetail
from app.utils.time import utc_now

logger = get_logger(__name__)


class AppError(Exception):
    """Base exception for expected application errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "APPLICATION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code or self.status_code
        self.code = code or self.code
        self.context = context or {}
        super().__init__(message)


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "AUTHENTICATION_REQUIRED"


class AuthorizationError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "AUTHORIZATION_FAILED"


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "RESOURCE_NOT_FOUND"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "RESOURCE_CONFLICT"


class ServiceUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "SERVICE_UNAVAILABLE"


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _error_payload(
    *,
    request: Request,
    status_code: int,
    errors: list[ErrorDetail],
) -> JSONResponse:
    payload = APIResponse(
        data=None,
        meta={
            "request_id": _request_id(request),
            "timestamp": utc_now().isoformat(),
        },
        errors=errors,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "application_error",
        extra={
            "request_id": _request_id(request),
            "error_code": exc.code,
            "status_code": exc.status_code,
            "context": exc.context,
        },
    )
    return _error_payload(
        request=request,
        status_code=exc.status_code,
        errors=[ErrorDetail(code=exc.code, message=exc.message)],
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return _error_payload(
        request=request,
        status_code=exc.status_code,
        errors=[ErrorDetail(code="HTTP_ERROR", message=str(exc.detail))],
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        ErrorDetail(
            code="VALIDATION_ERROR",
            message=error.get("msg", "Invalid request value."),
            field=".".join(str(part) for part in error.get("loc", []) if part != "body") or None,
        )
        for error in exc.errors()
    ]
    return _error_payload(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        errors=errors,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_exception",
        extra={
            "request_id": _request_id(request),
            "path": request.url.path,
        },
    )
    return _error_payload(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors=[ErrorDetail(code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred.")],
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all application exception handlers."""

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
