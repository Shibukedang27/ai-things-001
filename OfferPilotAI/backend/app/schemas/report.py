"""Report API schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import ReportStatus
from app.schemas.common import ORMModel


class ReportCreate(BaseModel):
    """Request body for report creation."""

    user_id: str
    interview_id: str
    title: str = Field(..., min_length=2, max_length=180)
    summary: str = Field(..., min_length=1)
    status: ReportStatus = ReportStatus.DRAFT
    overall_score: Decimal | None = Field(default=None, ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    improvement_areas: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    version: int = Field(default=1, ge=1)


class ReportUpdate(BaseModel):
    """Request body for report updates."""

    title: str | None = Field(default=None, min_length=2, max_length=180)
    summary: str | None = Field(default=None, min_length=1)
    status: ReportStatus | None = None
    overall_score: Decimal | None = Field(default=None, ge=0, le=100)
    strengths: list[str] | None = None
    improvement_areas: list[str] | None = None
    recommendations: list[str] | None = None
    version: int | None = Field(default=None, ge=1)


class ReportRead(ORMModel):
    """Persisted report response."""

    id: str
    user_id: str
    interview_id: str
    title: str
    summary: str
    status: ReportStatus
    overall_score: Decimal | None
    strengths: list[str]
    improvement_areas: list[str]
    recommendations: list[str]
    version: int
    created_at: datetime
    updated_at: datetime
