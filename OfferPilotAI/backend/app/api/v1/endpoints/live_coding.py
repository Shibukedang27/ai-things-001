"""Live coding endpoints."""

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_principal, get_db_session, get_request_settings
from app.core.config import Settings
from app.domain.enums import CodingLanguage
from app.schemas.coding import (
    CodeAnalysisRequest,
    CodeAnalysisResult,
    CodeRunRequest,
    CodeRunResult,
    CodeSubmissionCreate,
    CodeSubmissionListResponse,
    CodeSubmissionRead,
    LiveCodingOptions,
)
from app.schemas.common import APIResponse
from app.services.auth import AuthenticatedPrincipal
from app.services.coding import LiveCodingService

router = APIRouter()


def get_live_coding_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> LiveCodingService:
    settings: Settings = get_request_settings(request)
    return LiveCodingService(session, settings)


@router.get(
    "/options",
    response_model=APIResponse[LiveCodingOptions],
    summary="List live coding languages and analysis outputs",
)
async def live_coding_options(
    _: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LiveCodingService = Depends(get_live_coding_service),
) -> APIResponse[LiveCodingOptions]:
    return APIResponse(data=service.options())


@router.post(
    "/run",
    response_model=APIResponse[CodeRunResult],
    summary="Run code in the selected language",
)
async def run_code(
    payload: CodeRunRequest,
    _: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LiveCodingService = Depends(get_live_coding_service),
) -> APIResponse[CodeRunResult]:
    return APIResponse(data=await service.run_code(payload))


@router.post(
    "/analyze",
    response_model=APIResponse[CodeAnalysisResult],
    summary="Analyze code for complexity, bugs, and improvements",
)
async def analyze_code(
    payload: CodeAnalysisRequest,
    _: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LiveCodingService = Depends(get_live_coding_service),
) -> APIResponse[CodeAnalysisResult]:
    return APIResponse(data=await service.analyze_code(payload))


@router.post(
    "/submissions",
    response_model=APIResponse[CodeSubmissionRead],
    status_code=status.HTTP_201_CREATED,
    summary="Store a live-coding submission",
)
async def create_submission(
    payload: CodeSubmissionCreate,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LiveCodingService = Depends(get_live_coding_service),
) -> APIResponse[CodeSubmissionRead]:
    return APIResponse(data=await service.create_submission(principal=principal, payload=payload))


@router.get(
    "/submissions",
    response_model=APIResponse[CodeSubmissionListResponse],
    summary="List live-coding submissions",
)
async def list_submissions(
    language: CodingLanguage | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=100),
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LiveCodingService = Depends(get_live_coding_service),
) -> APIResponse[CodeSubmissionListResponse]:
    return APIResponse(
        data=await service.list_submissions(
            principal=principal,
            language=language,
            offset=offset,
            limit=limit,
        )
    )


@router.get(
    "/submissions/{submission_id}",
    response_model=APIResponse[CodeSubmissionRead],
    summary="Get a live-coding submission",
)
async def get_submission(
    submission_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: LiveCodingService = Depends(get_live_coding_service),
) -> APIResponse[CodeSubmissionRead]:
    return APIResponse(data=await service.get_submission(principal=principal, submission_id=submission_id))
