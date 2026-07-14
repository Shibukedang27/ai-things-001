"""AI evaluation endpoints."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_principal, get_db_session
from app.schemas.common import APIResponse
from app.schemas.evaluation import (
    AnswerEvaluationRead,
    EvaluateAnswerResponse,
    EvaluateInterviewResponse,
    EvaluationOptions,
)
from app.services.auth import AuthenticatedPrincipal
from app.services.evaluation import AIEvaluationService

router = APIRouter()


def get_evaluation_service(session: AsyncSession = Depends(get_db_session)) -> AIEvaluationService:
    return AIEvaluationService(session)


@router.get(
    "/options",
    response_model=APIResponse[EvaluationOptions],
    summary="List AI evaluation dimensions and generated outputs",
)
async def evaluation_options(
    _: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AIEvaluationService = Depends(get_evaluation_service),
) -> APIResponse[EvaluationOptions]:
    return APIResponse(data=service.options())


@router.get(
    "/answers/{answer_id}",
    response_model=APIResponse[AnswerEvaluationRead],
    summary="Get answer evaluation",
)
async def get_answer_evaluation(
    answer_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AIEvaluationService = Depends(get_evaluation_service),
) -> APIResponse[AnswerEvaluationRead]:
    return APIResponse(data=await service.get_answer_evaluation(principal=principal, answer_id=answer_id))


@router.post(
    "/answers/{answer_id}",
    response_model=APIResponse[EvaluateAnswerResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Evaluate one answer",
)
async def evaluate_answer(
    answer_id: str,
    force: bool = Query(default=False),
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AIEvaluationService = Depends(get_evaluation_service),
) -> APIResponse[EvaluateAnswerResponse]:
    return APIResponse(data=await service.evaluate_answer(principal=principal, answer_id=answer_id, force=force))


@router.get(
    "/interviews/{interview_id}",
    response_model=APIResponse[EvaluateInterviewResponse],
    summary="List interview answer evaluations",
)
async def list_interview_evaluations(
    interview_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AIEvaluationService = Depends(get_evaluation_service),
) -> APIResponse[EvaluateInterviewResponse]:
    return APIResponse(data=await service.list_interview_evaluations(principal=principal, interview_id=interview_id))


@router.post(
    "/interviews/{interview_id}",
    response_model=APIResponse[EvaluateInterviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Evaluate every answer in an interview",
)
async def evaluate_interview(
    interview_id: str,
    force: bool = Query(default=False),
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AIEvaluationService = Depends(get_evaluation_service),
) -> APIResponse[EvaluateInterviewResponse]:
    return APIResponse(data=await service.evaluate_interview(principal=principal, interview_id=interview_id, force=force))
