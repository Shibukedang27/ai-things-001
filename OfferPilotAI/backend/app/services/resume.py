"""Resume analyzer application service."""

from __future__ import annotations

from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AppError, NotFoundError
from app.repositories import ResumeAnalysisRepository
from app.schemas.resume import (
    ResumeAnalysisListResponse,
    ResumeAnalysisPayload,
    ResumeAnalysisRead,
    ResumeAnalyzerOptions,
    ResumeTextAnalyzeRequest,
)
from app.services.auth import AuthenticatedPrincipal
from app.services.resume_provider import HeuristicResumeAnalyzerProvider, ResumeAnalyzerInput


class ResumeAnalyzerService:
    """Application service for resume PDF analysis and job-description matching."""

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        provider: HeuristicResumeAnalyzerProvider | None = None,
    ) -> None:
        self.session = session
        self.settings = settings
        self.repository = ResumeAnalysisRepository(session)
        self.provider = provider or HeuristicResumeAnalyzerProvider()

    def options(self) -> ResumeAnalyzerOptions:
        return ResumeAnalyzerOptions(
            accepted_file_types=["application/pdf"],
            max_pdf_bytes=self.settings.resume_pdf_max_bytes,
            max_resume_text_chars=self.settings.resume_text_max_chars,
            generated_outputs=[
                "skills",
                "missing_skills",
                "job_description_comparison",
                "ats_score",
                "resume_suggestions",
                "resume_based_interview_questions",
                "skill_gap_report",
            ],
            analyzer_version=self.provider.analyzer_version,
        )

    async def analyze_pdf(
        self,
        *,
        principal: AuthenticatedPrincipal,
        resume_file: UploadFile,
        job_description: str | None,
    ) -> ResumeAnalysisRead:
        file_bytes = await resume_file.read()
        self._validate_pdf_upload(resume_file=resume_file, file_bytes=file_bytes)
        resume_text = self._extract_pdf_text(file_bytes)
        return await self._create_analysis(
            principal=principal,
            filename=resume_file.filename or "resume.pdf",
            content_type=resume_file.content_type or "application/pdf",
            file_size=len(file_bytes),
            resume_text=resume_text,
            job_description=job_description,
            metadata={"source": "pdf_upload"},
        )

    async def analyze_text(
        self,
        *,
        principal: AuthenticatedPrincipal,
        payload: ResumeTextAnalyzeRequest,
    ) -> ResumeAnalysisRead:
        self._validate_text(payload.resume_text)
        return await self._create_analysis(
            principal=principal,
            filename=payload.filename,
            content_type="text/plain",
            file_size=len(payload.resume_text.encode("utf-8")),
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            metadata={"source": "text_import"},
        )

    async def list_analyses(
        self,
        *,
        principal: AuthenticatedPrincipal,
        offset: int,
        limit: int,
    ) -> ResumeAnalysisListResponse:
        analyses = list(await self.repository.list_for_user(user_id=principal.user.id, offset=offset, limit=limit))
        return ResumeAnalysisListResponse(
            analyses=[ResumeAnalysisRead.model_validate(analysis) for analysis in analyses],
            count=len(analyses),
        )

    async def get_analysis(self, *, principal: AuthenticatedPrincipal, analysis_id: str) -> ResumeAnalysisRead:
        analysis = await self.repository.get_for_user(analysis_id=analysis_id, user_id=principal.user.id)
        if not analysis:
            raise NotFoundError("Resume analysis not found.")
        return ResumeAnalysisRead.model_validate(analysis)

    async def _create_analysis(
        self,
        *,
        principal: AuthenticatedPrincipal,
        filename: str,
        content_type: str,
        file_size: int,
        resume_text: str,
        job_description: str | None,
        metadata: dict,
    ) -> ResumeAnalysisRead:
        result = await self.provider.analyze(
            ResumeAnalyzerInput(
                resume_text=resume_text,
                job_description=job_description,
                filename=filename,
            )
        )
        analysis = await self.repository.create(
            self._analysis_values(
                principal=principal,
                filename=filename,
                content_type=content_type,
                file_size=file_size,
                resume_text=resume_text,
                job_description=job_description,
                result=result,
                metadata=metadata,
            )
        )
        await self.session.commit()
        await self.session.refresh(analysis)
        return ResumeAnalysisRead.model_validate(analysis)

    def _analysis_values(
        self,
        *,
        principal: AuthenticatedPrincipal,
        filename: str,
        content_type: str,
        file_size: int,
        resume_text: str,
        job_description: str | None,
        result: ResumeAnalysisPayload,
        metadata: dict,
    ) -> dict:
        return {
            "user_id": principal.user.id,
            "filename": filename,
            "content_type": content_type,
            "file_size": file_size,
            "resume_text": resume_text,
            "job_description": job_description,
            "extracted_skills": [skill.model_dump(mode="json") for skill in result.extracted_skills],
            "matched_skills": [skill.model_dump(mode="json") for skill in result.matched_skills],
            "missing_skills": [skill.model_dump(mode="json") for skill in result.missing_skills],
            "ats_score": result.ats_score,
            "resume_suggestions": result.resume_suggestions,
            "interview_questions": [question.model_dump(mode="json") for question in result.interview_questions],
            "skill_gap_report": result.skill_gap_report.model_dump(mode="json"),
            "analysis_summary": result.analysis_summary,
            "analyzer_version": result.analyzer_version,
            "metadata_json": metadata,
        }

    def _validate_pdf_upload(self, *, resume_file: UploadFile, file_bytes: bytes) -> None:
        filename = resume_file.filename or ""
        content_type = resume_file.content_type or ""
        if content_type != "application/pdf" and not filename.lower().endswith(".pdf"):
            raise AppError("Resume upload must be a PDF file.", status_code=400, code="RESUME_INVALID_FILE_TYPE")
        if not file_bytes:
            raise AppError("Resume PDF is empty.", status_code=400, code="RESUME_EMPTY_FILE")
        if len(file_bytes) > self.settings.resume_pdf_max_bytes:
            raise AppError("Resume PDF exceeds the configured file size limit.", status_code=400, code="RESUME_FILE_TOO_LARGE")

    def _extract_pdf_text(self, file_bytes: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(file_bytes))
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as exc:
                    raise AppError("Encrypted resume PDFs are not supported.", status_code=400, code="RESUME_ENCRYPTED") from exc
            text = "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except (PdfReadError, ValueError) as exc:
            raise AppError("Resume PDF could not be parsed.", status_code=400, code="RESUME_PARSE_FAILED") from exc

        self._validate_text(text)
        return text[: self.settings.resume_text_max_chars]

    def _validate_text(self, resume_text: str) -> None:
        if not resume_text or len(resume_text.split()) < 10:
            raise AppError(
                "Resume text could not be extracted with enough content to analyze.",
                status_code=400,
                code="RESUME_TEXT_TOO_SHORT",
            )
        if len(resume_text) > self.settings.resume_text_max_chars:
            raise AppError(
                "Resume text exceeds the configured analysis limit.",
                status_code=400,
                code="RESUME_TEXT_TOO_LARGE",
            )
