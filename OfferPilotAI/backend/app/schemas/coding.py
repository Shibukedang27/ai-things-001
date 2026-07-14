"""Live coding API schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.enums import CodeRunStatus, CodingLanguage
from app.schemas.common import ORMModel


class CodeRunRequest(BaseModel):
    """Run source code in a constrained language runner."""

    language: CodingLanguage
    source_code: str = Field(..., min_length=1, max_length=50_000)
    stdin: str = Field(default="", max_length=20_000)
    expected_output: str | None = Field(default=None, max_length=20_000)
    timeout_seconds: float = Field(default=3.0, ge=0.5, le=10)

    @field_validator("source_code")
    @classmethod
    def source_code_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Source code cannot be blank.")
        return value


class CodeAnalysisRequest(BaseModel):
    """Analyze source code without running it."""

    language: CodingLanguage
    source_code: str = Field(..., min_length=1, max_length=50_000)
    prompt: str | None = Field(default=None, max_length=4_000)

    @field_validator("source_code")
    @classmethod
    def source_code_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Source code cannot be blank.")
        return value


class CodeSubmissionCreate(CodeRunRequest):
    """Create a persisted live-coding submission."""

    prompt_title: str = Field(default="Untitled Coding Challenge", min_length=2, max_length=180)
    prompt: str | None = Field(default=None, max_length=4_000)
    interview_id: str | None = Field(default=None, max_length=36)
    run_code: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class CodeRunResult(BaseModel):
    """Code execution result."""

    language: CodingLanguage
    status: CodeRunStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    execution_time_ms: int | None = None
    memory_kb: int | None = None
    passed: bool | None = None


class CodeIssue(BaseModel):
    """Static analysis issue."""

    severity: Literal["info", "warning", "error"]
    message: str
    line: int | None = None
    rule: str


class CodeAnalysisResult(BaseModel):
    """Code analysis and optimization response."""

    language: CodingLanguage
    time_complexity: str
    space_complexity: str
    bugs: list[CodeIssue]
    optimized_code: str
    improvement_explanation: str
    improvement_suggestions: list[str]
    quality_score: Decimal = Field(..., ge=0, le=100)
    observations: list[str] = Field(default_factory=list)
    analyzer_version: str


class CodeSubmissionRead(ORMModel):
    """Persisted live-coding submission response."""

    id: str
    user_id: str
    interview_id: str | None
    language: CodingLanguage
    prompt_title: str
    prompt: str | None
    source_code: str
    stdin: str
    expected_output: str | None
    status: CodeRunStatus
    stdout: str
    stderr: str
    exit_code: int | None
    execution_time_ms: int | None
    memory_kb: int | None
    time_complexity: str
    space_complexity: str
    bugs: list[dict[str, Any]]
    optimized_code: str
    improvement_explanation: str
    analysis: dict[str, Any]
    metadata_json: dict[str, Any]
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime


class CodeSubmissionListResponse(BaseModel):
    """Paginated submission list."""

    submissions: list[CodeSubmissionRead]
    count: int


class LiveCodingOptions(BaseModel):
    """Live coding module metadata."""

    languages: list[CodingLanguage]
    execution_statuses: list[CodeRunStatus]
    analysis_outputs: list[str]
    max_source_chars: int
    max_stdin_chars: int
    default_timeout_seconds: float
    max_timeout_seconds: float
    execution_enabled: bool
