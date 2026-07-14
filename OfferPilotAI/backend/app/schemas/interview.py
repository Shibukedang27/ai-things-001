"""Interview API schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.domain.enums import InterviewSessionStatus, InterviewStatus, InterviewType, SeniorityLevel
from app.schemas.common import ORMModel


class InterviewTemplateRead(BaseModel):
    """Public interview template metadata."""

    id: str
    name: str
    interview_type: InterviewType
    recommended_duration_minutes: int
    description: str


class InterviewSessionCreate(BaseModel):
    """Request body for creating an interview session draft."""

    role_title: str = Field(..., min_length=2, max_length=160, examples=["Senior Backend Engineer"])
    company_name: str | None = Field(default=None, max_length=160, examples=["Acme AI"])
    seniority: SeniorityLevel = SeniorityLevel.MID
    interview_type: InterviewType = InterviewType.MIXED
    focus_areas: list[str] = Field(default_factory=list, max_length=8)
    duration_minutes: int = Field(default=45, ge=15, le=180)

    @field_validator("focus_areas")
    @classmethod
    def validate_focus_areas(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value if item.strip()]
        if len(set(item.lower() for item in normalized)) != len(normalized):
            raise ValueError("Focus areas must be unique.")
        return normalized


class InterviewCreate(InterviewSessionCreate):
    """Request body for persisted interview creation."""

    user_id: str = Field(..., min_length=1)
    title: str | None = Field(default=None, max_length=180)
    status: InterviewStatus = InterviewStatus.DRAFT
    scheduled_at: datetime | None = None


class InterviewUpdate(BaseModel):
    """Request body for interview updates."""

    title: str | None = Field(default=None, min_length=2, max_length=180)
    role_title: str | None = Field(default=None, min_length=2, max_length=160)
    company_name: str | None = Field(default=None, max_length=160)
    seniority: SeniorityLevel | None = None
    interview_type: InterviewType | None = None
    status: InterviewStatus | None = None
    focus_areas: list[str] | None = Field(default=None, max_length=8)
    duration_minutes: int | None = Field(default=None, ge=15, le=180)
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    overall_score: Decimal | None = Field(default=None, ge=0, le=100)
    is_archived: bool | None = None

    @field_validator("focus_areas")
    @classmethod
    def validate_optional_focus_areas(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        normalized = [item.strip() for item in value if item.strip()]
        if len(set(item.lower() for item in normalized)) != len(normalized):
            raise ValueError("Focus areas must be unique.")
        return normalized


class InterviewRead(ORMModel):
    """Persisted interview response."""

    id: str
    user_id: str
    title: str
    role_title: str
    company_name: str | None
    seniority: SeniorityLevel
    interview_type: InterviewType
    status: InterviewStatus
    focus_areas: list[str]
    duration_minutes: int
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    overall_score: Decimal | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class InterviewSessionRead(ORMModel):
    """Interview session response."""

    id: str
    role_title: str
    company_name: str | None
    seniority: SeniorityLevel
    interview_type: InterviewType
    status: InterviewSessionStatus
    focus_areas: list[str]
    duration_minutes: int
    question_count: int
