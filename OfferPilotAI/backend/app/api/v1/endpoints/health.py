"""Health and readiness endpoints."""

from fastapi import APIRouter, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.schemas.common import APIResponse
from app.schemas.health import HealthStatus, ReadinessStatus
from app.services.health import HealthService

router = APIRouter()


@router.get(
    "/health",
    response_model=APIResponse[HealthStatus],
    summary="Get service health",
)
async def health_check(request: Request) -> APIResponse[HealthStatus]:
    service = HealthService(request.app.state.settings)
    return APIResponse(data=service.get_health())


@router.get(
    "/health/live",
    response_model=APIResponse[HealthStatus],
    summary="Check liveness",
)
async def liveness_check(request: Request) -> APIResponse[HealthStatus]:
    service = HealthService(request.app.state.settings)
    return APIResponse(data=service.get_health())


@router.get(
    "/health/ready",
    response_model=APIResponse[ReadinessStatus],
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "A dependency is unavailable."}},
    summary="Check readiness",
)
async def readiness_check(request: Request) -> APIResponse[ReadinessStatus] | JSONResponse:
    service = HealthService(request.app.state.settings)
    readiness = await service.get_readiness()
    response = APIResponse(data=readiness)

    if readiness.ready:
        return response

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=jsonable_encoder(response),
    )
