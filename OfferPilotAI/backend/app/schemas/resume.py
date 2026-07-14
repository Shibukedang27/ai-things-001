"""Resume analyzer API schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORMModel


class ResumeSkill(BaseModel):
    """Detected resume or job-description skill."""

    name: str
    category: str
    evidence_count: int = Field(..., ge=1)
    confidence: Decimal = Field(..., ge=0, le=100)


class MissingSkill(BaseModel):
    """Skill required by the job description but missing from the resume."""

    name: str
    category: str
    priority: Literal["high", "medium", "low"]
    reason: str


class ResumeInterviewQuestion(BaseModel):
    """Generated interview question based on resume and gaps."""

    question: str
    category: str
    difficulty: Literal["easy", "medium", "hard"]
    signal: str


class SkillGapReport(BaseModel):
    """Structured skill gap report."""

    match_rate: Decimal = Field(..., ge=0, le=100)
    strongest_categories: list[str]
    weakest_categories: list[str]
    priority_gaps: list[MissingSkill]
    recommended_focus: list[str]
    summary: str


class ResumeAnalysisPayload(BaseModel):
    """Analyzer result payload."""

    extracted_skills: list[ResumeSkill]
    matched_skills: list[ResumeSkill]
    missing_skills: list[MissingSkill]
    ats_score: Decimal = Field(..., ge=0, le=100)
    resume_suggestions: list[str]
    interview_questions: list[ResumeInterviewQuestion]
    skill_gap_report: SkillGapReport
    analysis_summary: str
    analyzer_version: str


class ResumeTextAnalyzeRequest(BaseModel):
    """Analyze pasted resume text. Useful for tests and non-PDF imports."""

    resume_text: str = Field(..., min_length=50, max_length=120_000)
    job_description: str | None = Field(default=None, max_length=40_000)
    filename: str = Field(default="pasted-resume.txt", min_length=2, max_length=255)

    @field_validator("resume_text")
    @classmethod
    def resume_text_must_have_signal(cls, value: str) -> str:
        if len(value.split()) < 10:
            raise ValueError("Resume text must contain enough words to analyze.")
        return value


class ResumeAnalysisRead(ORMModel):
    """Persisted resume analysis response."""

    id: str
    user_id: str
    filename: str
    content_type: str
    file_size: int
    resume_text: str
    job_description: str | None
    extracted_skills: list[dict[str, Any]]
    matched_skills: list[dict[str, Any]]
    missing_skills: list[dict[str, Any]]
    ats_score: Decimal
    resume_suggestions: list[str]
    interview_questions: list[dict[str, Any]]
    skill_gap_report: dict[str, Any]
    analysis_summary: str
    analyzer_version: str
    metadata_json: dict[str, Any]
    analyzed_at: datetime
    created_at: datetime
    updated_at: datetime


class ResumeAnalysisListResponse(BaseModel):
    """List of stored resume analyses."""

    analyses: list[ResumeAnalysisRead]
    count: int


class ResumeAnalyzerOptions(BaseModel):
    """Resume analyzer metadata."""

    accepted_file_types: list[str]
    max_pdf_bytes: int
    max_resume_text_chars: int
    generated_outputs: list[str]
    analyzer_version: str
