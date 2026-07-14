"""Learning roadmap API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import RoadmapStatus
from app.schemas.common import ORMModel


class LearningRoadmapCreate(BaseModel):
    """Request body for learning roadmap creation."""

    user_id: str
    report_id: str | None = None
    title: str = Field(..., min_length=2, max_length=180)
    target_role: str | None = Field(default=None, max_length=160)
    status: RoadmapStatus = RoadmapStatus.DRAFT
    estimated_weeks: int = Field(default=4, ge=1, le=104)
    recommended_topics: list[str] = Field(default_factory=list)
    milestones: list[dict[str, Any]] = Field(default_factory=list)
    weak_topics: list[dict[str, Any]] = Field(default_factory=list)
    leetcode_problems: list[dict[str, Any]] = Field(default_factory=list)
    hackerrank_problems: list[dict[str, Any]] = Field(default_factory=list)
    books: list[dict[str, Any]] = Field(default_factory=list)
    courses: list[dict[str, Any]] = Field(default_factory=list)
    youtube_videos: list[dict[str, Any]] = Field(default_factory=list)
    daily_practice_plan: list[dict[str, Any]] = Field(default_factory=list)
    weekly_roadmap: list[dict[str, Any]] = Field(default_factory=list)
    monthly_roadmap: list[dict[str, Any]] = Field(default_factory=list)
    source_summary: dict[str, Any] = Field(default_factory=dict)


class LearningRoadmapUpdate(BaseModel):
    """Request body for learning roadmap updates."""

    report_id: str | None = None
    title: str | None = Field(default=None, min_length=2, max_length=180)
    target_role: str | None = Field(default=None, max_length=160)
    status: RoadmapStatus | None = None
    estimated_weeks: int | None = Field(default=None, ge=1, le=104)
    recommended_topics: list[str] | None = None
    milestones: list[dict[str, Any]] | None = None
    weak_topics: list[dict[str, Any]] | None = None
    leetcode_problems: list[dict[str, Any]] | None = None
    hackerrank_problems: list[dict[str, Any]] | None = None
    books: list[dict[str, Any]] | None = None
    courses: list[dict[str, Any]] | None = None
    youtube_videos: list[dict[str, Any]] | None = None
    daily_practice_plan: list[dict[str, Any]] | None = None
    weekly_roadmap: list[dict[str, Any]] | None = None
    monthly_roadmap: list[dict[str, Any]] | None = None
    source_summary: dict[str, Any] | None = None


class LearningRoadmapRead(ORMModel):
    """Persisted learning roadmap response."""

    id: str
    user_id: str
    report_id: str | None
    title: str
    target_role: str | None
    status: RoadmapStatus
    estimated_weeks: int
    recommended_topics: list[str]
    milestones: list[dict[str, Any]]
    weak_topics: list[dict[str, Any]]
    leetcode_problems: list[dict[str, Any]]
    hackerrank_problems: list[dict[str, Any]]
    books: list[dict[str, Any]]
    courses: list[dict[str, Any]]
    youtube_videos: list[dict[str, Any]]
    daily_practice_plan: list[dict[str, Any]]
    weekly_roadmap: list[dict[str, Any]]
    monthly_roadmap: list[dict[str, Any]]
    source_summary: dict[str, Any]
    created_at: datetime
    updated_at: datetime
