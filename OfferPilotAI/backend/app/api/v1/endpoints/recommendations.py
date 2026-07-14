"""Learning recommendation endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_principal, get_db_session
from app.schemas.common import APIResponse
from app.schemas.recommendation import (
    GenerateRoadmapRequest,
    LearningRecommendationOptions,
    LearningRecommendationResponse,
)
from app.services.auth import AuthenticatedPrincipal
from app.services.recommendation import LearningRecommendationService

router = APIRouter()


def get_recommendation_service(session: AsyncSession = Depends(get_db_session)) -> LearningRecommendationService:
    return LearningRecommendationService(session)


@router.get(
    "/options",
    response_model=APIResponse[LearningRecommendationOptions],
    summary="List learning recommendation outputs",
)
async def recommendation_options(
    _: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LearningRecommendationService = Depends(get_recommendation_service),
) -> APIResponse[LearningRecommendationOptions]:
    return APIResponse(data=service.options())


@router.post(
    "/roadmaps",
    response_model=APIResponse[LearningRecommendationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate a personalized learning roadmap",
)
async def generate_roadmap(
    payload: GenerateRoadmapRequest,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LearningRecommendationService = Depends(get_recommendation_service),
) -> APIResponse[LearningRecommendationResponse]:
    return APIResponse(data=await service.generate_roadmap(principal=principal, payload=payload))


@router.get(
    "/roadmaps/latest",
    response_model=APIResponse[LearningRecommendationResponse],
    summary="Get latest generated learning roadmap",
)
async def latest_roadmap(
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LearningRecommendationService = Depends(get_recommendation_service),
) -> APIResponse[LearningRecommendationResponse]:
    return APIResponse(data=await service.latest_roadmap(principal=principal))
