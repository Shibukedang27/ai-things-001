"""Analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_principal, get_db_session
from app.schemas.analytics import AnalyticsOverview
from app.schemas.common import APIResponse
from app.services.analytics import AnalyticsAggregationService
from app.services.auth import AuthenticatedPrincipal

router = APIRouter()


def get_analytics_service(session: AsyncSession = Depends(get_db_session)) -> AnalyticsAggregationService:
    return AnalyticsAggregationService(session)


@router.get(
    "/overview",
    response_model=APIResponse[AnalyticsOverview],
    summary="Generate interview performance analytics",
)
async def analytics_overview(
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AnalyticsAggregationService = Depends(get_analytics_service),
) -> APIResponse[AnalyticsOverview]:
    return APIResponse(data=await service.overview(principal=principal))
