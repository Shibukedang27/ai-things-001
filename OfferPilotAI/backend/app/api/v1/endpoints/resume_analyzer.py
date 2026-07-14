"""Resume analyzer endpoints."""

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_principal, get_db_session, get_request_settings
from app.core.config import Settings
from app.schemas.common import APIResponse
from app.schemas.resume import (
    ResumeAnalysisListResponse,
    ResumeAnalysisRead,
    ResumeAnalyzerOptions,
    ResumeTextAnalyzeRequest,
)
from app.services.auth import AuthenticatedPrincipal
from app.services.resume import ResumeAnalyzerService

router = APIRouter()


def get_resume_analyzer_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> ResumeAnalyzerService:
    settings: Settings = get_request_settings(request)
    return ResumeAnalyzerService(session, settings)


@router.get(
    "/options",
    response_model=APIResponse[ResumeAnalyzerOptions],
    summary="List resume analyzer capabilities",
)
async def resume_analyzer_options(
    _: AuthenticatedPrincipal = Depends(get_current_principal),
    service: ResumeAnalyzerService = Depends(get_resume_analyzer_service),
) -> APIResponse[ResumeAnalyzerOptions]:
    return APIResponse(data=service.options())


@router.post(
    "/analyze",
    response_model=APIResponse[ResumeAnalysisRead],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and analyze a resume PDF",
)
async def analyze_resume_pdf(
    resume_file: UploadFile = File(..., description="Resume PDF file"),
    job_description: str | None = Form(default=None),
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: ResumeAnalyzerService = Depends(get_resume_analyzer_service),
) -> APIResponse[ResumeAnalysisRead]:
    return APIResponse(
        data=await service.analyze_pdf(
            principal=principal,
            resume_file=resume_file,
            job_description=job_description,
        )
    )


@router.post(
    "/analyze-text",
    response_model=APIResponse[ResumeAnalysisRead],
    status_code=status.HTTP_201_CREATED,
    summary="Analyze resume text",
)
async def analyze_resume_text(
    payload: ResumeTextAnalyzeRequest,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: ResumeAnalyzerService = Depends(get_resume_analyzer_service),
) -> APIResponse[ResumeAnalysisRead]:
    return APIResponse(data=await service.analyze_text(principal=principal, payload=payload))


@router.get(
    "/analyses",
    response_model=APIResponse[ResumeAnalysisListResponse],
    summary="List resume analyses",
)
async def list_resume_analyses(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=100),
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: ResumeAnalyzerService = Depends(get_resume_analyzer_service),
) -> APIResponse[ResumeAnalysisListResponse]:
    return APIResponse(data=await service.list_analyses(principal=principal, offset=offset, limit=limit))


@router.get(
    "/analyses/{analysis_id}",
    response_model=APIResponse[ResumeAnalysisRead],
    summary="Get resume analysis",
)
async def get_resume_analysis(
    analysis_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: ResumeAnalyzerService = Depends(get_resume_analyzer_service),
) -> APIResponse[ResumeAnalysisRead]:
    return APIResponse(data=await service.get_analysis(principal=principal, analysis_id=analysis_id))
