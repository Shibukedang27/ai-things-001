"""Analytics API schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TopicAccuracyPoint(BaseModel):
    """Topic-wise accuracy summary."""

    topic: str
    accuracy: Decimal = Field(..., ge=0, le=100)
    attempts: int = Field(..., ge=0)
    average_score: Decimal = Field(..., ge=0, le=100)
    trend: Decimal


class ProgressPoint(BaseModel):
    """Weekly or monthly progress point."""

    label: str
    average_score: Decimal = Field(..., ge=0, le=100)
    interview_count: int = Field(..., ge=0)
    accuracy: Decimal = Field(..., ge=0, le=100)


class HeatMapCell(BaseModel):
    """Practice heat map cell."""

    day: str
    hour: int = Field(..., ge=0, le=23)
    value: int = Field(..., ge=0)
    intensity: Decimal = Field(..., ge=0, le=1)


class RadarMetric(BaseModel):
    """Radar chart metric."""

    metric: str
    score: Decimal = Field(..., ge=0, le=100)
    benchmark: Decimal = Field(..., ge=0, le=100)


class TrendPoint(BaseModel):
    """Strength or weakness trend point."""

    label: str
    score: Decimal = Field(..., ge=0, le=100)
    topic: str


class InterviewHistoryAnalyticsItem(BaseModel):
    """Interview history row for analytics views."""

    id: str
    title: str
    role_title: str
    status: str
    score: Decimal | None
    duration_minutes: int
    completed_at: datetime | None


class PerformanceGraphPoint(BaseModel):
    """Performance graph point across scoring dimensions."""

    label: str
    overall_score: Decimal = Field(..., ge=0, le=100)
    technical_accuracy: Decimal = Field(..., ge=0, le=100)
    communication: Decimal = Field(..., ge=0, le=100)
    problem_solving: Decimal = Field(..., ge=0, le=100)
    explanation_quality: Decimal = Field(..., ge=0, le=100)


class AnalyticsSummary(BaseModel):
    """High-level analytics summary."""

    average_score: Decimal = Field(..., ge=0, le=100)
    highest_score: Decimal = Field(..., ge=0, le=100)
    interview_count: int = Field(..., ge=0)
    strongest_topic: str | None
    weakest_topic: str | None


class AnalyticsOverview(BaseModel):
    """Complete analytics dashboard payload."""

    summary: AnalyticsSummary
    topic_wise_accuracy: list[TopicAccuracyPoint]
    weekly_progress: list[ProgressPoint]
    monthly_progress: list[ProgressPoint]
    heat_map: list[HeatMapCell]
    radar_chart: list[RadarMetric]
    weakness_trends: list[TrendPoint]
    strength_trends: list[TrendPoint]
    interview_history: list[InterviewHistoryAnalyticsItem]
    performance_graphs: list[PerformanceGraphPoint]
    generated_at: datetime
