"""Learning recommendation API schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.learning_roadmap import LearningRoadmapRead


class GenerateRoadmapRequest(BaseModel):
    """Request body for automatic roadmap generation."""

    interview_id: str | None = None
    target_role: str | None = Field(default=None, min_length=2, max_length=160)
    estimated_weeks: int = Field(default=4, ge=1, le=52)


class WeakTopic(BaseModel):
    """Detected weak topic."""

    topic: str
    category: str
    priority: str
    average_score: Decimal
    weak_dimensions: list[str]
    evidence_count: int


class LearningRecommendationOptions(BaseModel):
    """Recommendation engine metadata."""

    resource_types: list[str]
    roadmap_types: list[str]
    generated_from: list[str]
    supported_outputs: list[str]


class LearningRecommendationResponse(BaseModel):
    """Generated roadmap response."""

    roadmap: LearningRoadmapRead
    weak_topics: list[WeakTopic]
    generated_at: datetime
    source_summary: dict[str, Any]
