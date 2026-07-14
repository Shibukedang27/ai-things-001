from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.config import Settings, get_settings
from backend.dependencies.database import get_db
from backend.schemas.health import HealthResponse
from backend.services.health_service import HealthService

router = APIRouter()


@router.get("/live", response_model=HealthResponse, summary="Liveness probe")
def liveness(
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    return HealthService(session, settings).liveness()


@router.get("/ready", response_model=HealthResponse, summary="Readiness probe")
def readiness(
    session: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    return HealthService(session, settings).readiness()
