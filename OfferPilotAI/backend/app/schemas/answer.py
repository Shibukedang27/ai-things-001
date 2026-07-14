"""Answer API schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AnswerCreate(BaseModel):
    """Request body for answer creation."""

    user_id: str
    interview_id: str
    question_id: str
    transcript: str = Field(..., min_length=1)
    duration_seconds: int | None = Field(default=None, ge=0)
    score: Decimal | None = Field(default=None, ge=0, le=100)
    feedback: dict[str, Any] = Field(default_factory=dict)


class AnswerUpdate(BaseModel):
    """Request body for answer updates."""

    transcript: str | None = Field(default=None, min_length=1)
    duration_seconds: int | None = Field(default=None, ge=0)
    score: Decimal | None = Field(default=None, ge=0, le=100)
    feedback: dict[str, Any] | None = None


class AnswerRead(ORMModel):
    """Persisted answer response."""

    id: str
    user_id: str
    interview_id: str
    question_id: str
    transcript: str
    duration_seconds: int | None
    score: Decimal | None
    feedback: dict[str, Any]
    created_at: datetime
    updated_at: datetime
