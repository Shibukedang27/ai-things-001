"""Question catalog schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import DifficultyLevel, QuestionCategory
from app.schemas.common import ORMModel


class QuestionCategoryRead(BaseModel):
    """Supported question category."""

    id: QuestionCategory
    label: str
    description: str


class DifficultyLevelRead(BaseModel):
    """Supported question difficulty."""

    id: DifficultyLevel
    label: str
    description: str


class QuestionPromptRead(BaseModel):
    """Question prompt metadata."""

    id: str
    category: QuestionCategory
    difficulty: DifficultyLevel
    prompt: str = Field(..., min_length=10)


class QuestionCreate(BaseModel):
    """Request body for question creation."""

    interview_id: str | None = None
    category: QuestionCategory = QuestionCategory.BEHAVIORAL
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    prompt: str = Field(..., min_length=10)
    expected_signal: str | None = Field(default=None, max_length=80)
    rubric: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list, max_length=12)
    order_index: int = Field(default=0, ge=0)
    is_active: bool = True


class QuestionUpdate(BaseModel):
    """Request body for question updates."""

    interview_id: str | None = None
    category: QuestionCategory | None = None
    difficulty: DifficultyLevel | None = None
    prompt: str | None = Field(default=None, min_length=10)
    expected_signal: str | None = Field(default=None, max_length=80)
    rubric: dict[str, Any] | None = None
    tags: list[str] | None = Field(default=None, max_length=12)
    order_index: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class QuestionRead(ORMModel):
    """Persisted question response."""

    id: str
    interview_id: str | None
    category: QuestionCategory
    difficulty: DifficultyLevel
    prompt: str
    expected_signal: str | None
    rubric: dict[str, Any]
    tags: list[str]
    order_index: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
