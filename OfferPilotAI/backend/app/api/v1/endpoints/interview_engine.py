"""Interview engine endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_principal, get_db_session
from app.schemas.common import APIResponse
from app.schemas.interview_engine import (
    CompleteInterviewResponse,
    EngineQuestion,
    EngineSession,
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    SupportedEngineOptions,
)
from app.services.auth import AuthenticatedPrincipal
from app.services.interview_engine import InterviewEngineService

router = APIRouter()


def get_engine_service(session: AsyncSession = Depends(get_db_session)) -> InterviewEngineService:
    return InterviewEngineService(session)


@router.get(
    "/options",
    response_model=APIResponse[SupportedEngineOptions],
    summary="List supported interview engine options",
)
async def supported_options(
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[SupportedEngineOptions]:
    return APIResponse(data=service.supported_options())


@router.post(
    "/sessions",
    response_model=APIResponse[StartInterviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Start an interview engine session",
)
async def start_interview(
    payload: StartInterviewRequest,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[StartInterviewResponse]:
    return APIResponse(data=await service.start_interview(principal=principal, payload=payload))


@router.get(
    "/sessions/{interview_id}",
    response_model=APIResponse[EngineSession],
    summary="Get interview engine session state",
)
async def get_session(
    interview_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[EngineSession]:
    return APIResponse(data=await service.get_session(principal=principal, interview_id=interview_id))


@router.get(
    "/sessions/{interview_id}/current-question",
    response_model=APIResponse[EngineQuestion],
    summary="Get current interview question",
)
async def get_current_question(
    interview_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[EngineQuestion | None]:
    return APIResponse(data=await service.get_current_question(principal=principal, interview_id=interview_id))


@router.post(
    "/sessions/{interview_id}/answers",
    response_model=APIResponse[SubmitAnswerResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit answer for current question",
)
async def submit_answer(
    interview_id: str,
    payload: SubmitAnswerRequest,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[SubmitAnswerResponse]:
    return APIResponse(data=await service.submit_answer(principal=principal, interview_id=interview_id, payload=payload))


@router.post(
    "/sessions/{interview_id}/complete",
    response_model=APIResponse[CompleteInterviewResponse],
    summary="Complete an interview session without evaluation",
)
async def complete_interview(
    interview_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: InterviewEngineService = Depends(get_engine_service),
) -> APIResponse[CompleteInterviewResponse]:
    return APIResponse(data=await service.complete_interview(principal=principal, interview_id=interview_id))
