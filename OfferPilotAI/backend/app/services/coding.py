"""Live coding application service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AppError, NotFoundError
from app.domain.enums import CodeRunStatus, CodingLanguage
from app.models import CodeSubmission
from app.repositories import CodeSubmissionRepository
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
from app.services.auth import AuthenticatedPrincipal
from app.services.coding_analysis import CodeAnalysisInput, HeuristicCodeAnalysisProvider
from app.services.coding_execution import CodeExecutionInput, CodeExecutionService


class LiveCodingService:
    """Application service for live code execution, analysis, and submissions."""

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        *,
        executor: CodeExecutionService | None = None,
        analyzer: HeuristicCodeAnalysisProvider | None = None,
    ) -> None:
        self.session = session
        self.settings = settings
        self.repository = CodeSubmissionRepository(session)
        self.executor = executor or CodeExecutionService(execution_enabled=settings.live_code_execution_enabled)
        self.analyzer = analyzer or HeuristicCodeAnalysisProvider()

    def options(self) -> LiveCodingOptions:
        return LiveCodingOptions(
            languages=[CodingLanguage.PYTHON, CodingLanguage.JAVA, CodingLanguage.SQL],
            execution_statuses=[
                CodeRunStatus.SUCCESS,
                CodeRunStatus.FAILED,
                CodeRunStatus.TIMEOUT,
                CodeRunStatus.UNSUPPORTED,
                CodeRunStatus.SKIPPED,
            ],
            analysis_outputs=[
                "time_complexity",
                "space_complexity",
                "bugs",
                "optimized_code",
                "improvement_explanation",
                "improvement_suggestions",
                "quality_score",
            ],
            max_source_chars=self.settings.live_code_max_source_chars,
            max_stdin_chars=self.settings.live_code_max_stdin_chars,
            default_timeout_seconds=self.settings.live_code_default_timeout_seconds,
            max_timeout_seconds=self.settings.live_code_max_timeout_seconds,
            execution_enabled=self.settings.live_code_execution_enabled,
        )

    async def run_code(self, payload: CodeRunRequest) -> CodeRunResult:
        self._validate_limits(source_code=payload.source_code, stdin=payload.stdin)
        result = await self.executor.execute(
            CodeExecutionInput(
                language=payload.language,
                source_code=payload.source_code,
                stdin=payload.stdin,
                timeout_seconds=self._timeout(payload.timeout_seconds),
            )
        )
        passed = None
        if payload.expected_output is not None and result.status == CodeRunStatus.SUCCESS:
            passed = result.stdout.strip() == payload.expected_output.strip()
        return CodeRunResult(
            language=result.language,
            status=result.status,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            execution_time_ms=result.execution_time_ms,
            memory_kb=result.memory_kb,
            passed=passed,
        )

    async def analyze_code(self, payload: CodeAnalysisRequest) -> CodeAnalysisResult:
        self._validate_limits(source_code=payload.source_code, stdin="")
        return await self.analyzer.analyze(
            CodeAnalysisInput(
                language=payload.language,
                source_code=payload.source_code,
                prompt=payload.prompt,
            )
        )

    async def create_submission(
        self,
        *,
        principal: AuthenticatedPrincipal,
        payload: CodeSubmissionCreate,
    ) -> CodeSubmissionRead:
        if payload.interview_id:
            interview = await self.repository.get_interview_for_user(
                interview_id=payload.interview_id,
                user_id=principal.user.id,
            )
            if not interview:
                raise NotFoundError("Interview not found.")

        run_result = (
            await self.run_code(payload)
            if payload.run_code
            else CodeRunResult(language=payload.language, status=CodeRunStatus.SKIPPED)
        )
        analysis = await self.analyze_code(
            CodeAnalysisRequest(language=payload.language, source_code=payload.source_code, prompt=payload.prompt)
        )
        submission = await self.repository.create(self._submission_values(principal, payload, run_result, analysis))
        await self.session.commit()
        await self.session.refresh(submission)
        return CodeSubmissionRead.model_validate(submission)

    async def list_submissions(
        self,
        *,
        principal: AuthenticatedPrincipal,
        language: CodingLanguage | None,
        offset: int,
        limit: int,
    ) -> CodeSubmissionListResponse:
        submissions = list(
            await self.repository.list_for_user(
                user_id=principal.user.id,
                language=language.value if language else None,
                offset=offset,
                limit=limit,
            )
        )
        return CodeSubmissionListResponse(
            submissions=[CodeSubmissionRead.model_validate(submission) for submission in submissions],
            count=len(submissions),
        )

    async def get_submission(self, *, principal: AuthenticatedPrincipal, submission_id: str) -> CodeSubmissionRead:
        submission = await self.repository.get_for_user(submission_id=submission_id, user_id=principal.user.id)
        if not submission:
            raise NotFoundError("Code submission not found.")
        return CodeSubmissionRead.model_validate(submission)

    def _submission_values(
        self,
        principal: AuthenticatedPrincipal,
        payload: CodeSubmissionCreate,
        run_result: CodeRunResult,
        analysis: CodeAnalysisResult,
    ) -> dict:
        return {
            "user_id": principal.user.id,
            "interview_id": payload.interview_id,
            "language": payload.language.value,
            "prompt_title": payload.prompt_title,
            "prompt": payload.prompt,
            "source_code": payload.source_code,
            "stdin": payload.stdin,
            "expected_output": payload.expected_output,
            "status": run_result.status.value,
            "stdout": run_result.stdout,
            "stderr": run_result.stderr,
            "exit_code": run_result.exit_code,
            "execution_time_ms": run_result.execution_time_ms,
            "memory_kb": run_result.memory_kb,
            "time_complexity": analysis.time_complexity,
            "space_complexity": analysis.space_complexity,
            "bugs": [bug.model_dump(mode="json") for bug in analysis.bugs],
            "optimized_code": analysis.optimized_code,
            "improvement_explanation": analysis.improvement_explanation,
            "analysis": analysis.model_dump(mode="json"),
            "metadata_json": payload.metadata,
        }

    def _validate_limits(self, *, source_code: str, stdin: str) -> None:
        if len(source_code) > self.settings.live_code_max_source_chars:
            raise AppError(
                "Source code exceeds the configured live coding limit.",
                status_code=400,
                code="LIVE_CODING_SOURCE_TOO_LARGE",
            )
        if len(stdin) > self.settings.live_code_max_stdin_chars:
            raise AppError(
                "Standard input exceeds the configured live coding limit.",
                status_code=400,
                code="LIVE_CODING_STDIN_TOO_LARGE",
            )

    def _timeout(self, requested_timeout: float) -> float:
        return min(
            self.settings.live_code_max_timeout_seconds,
            max(0.5, requested_timeout or self.settings.live_code_default_timeout_seconds),
        )
