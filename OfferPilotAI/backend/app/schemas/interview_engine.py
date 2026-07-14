"""Interview engine API schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from app.domain.enums import DifficultyLevel, InterviewStatus


class EngineQuestionCategory(StrEnum):
    """Supported interview engine categories."""

    PYTHON = "python"
    JAVA = "java"
    SQL = "sql"
    DSA = "dsa"
    SYSTEM_DESIGN = "system_design"
    MACHINE_LEARNING = "machine_learning"
    DEEP_LEARNING = "deep_learning"
    NLP = "nlp"
    PROMPT_ENGINEERING = "prompt_engineering"
    BEHAVIORAL = "behavioral"
    HR = "hr"


class StartInterviewRequest(BaseModel):
    """Request body for starting an interview engine session."""

    role: str = Field(..., min_length=2, max_length=160, examples=["Senior Backend Engineer"])
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    duration_minutes: int = Field(default=45, ge=5, le=180)
    categories: list[EngineQuestionCategory] = Field(..., min_length=1, max_length=11)

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, value: list[EngineQuestionCategory]) -> list[EngineQuestionCategory]:
        if len(set(value)) != len(value):
            raise ValueError("Question categories must be unique.")
        return value


class EngineTimer(BaseModel):
    """Server-side interview timer snapshot."""

    duration_seconds: int
    elapsed_seconds: int
    remaining_seconds: int
    expired: bool
    started_at: datetime | None
    expires_at: datetime | None


class EngineQuestion(BaseModel):
    """Question generated for an interview engine session."""

    id: str
    category: EngineQuestionCategory
    difficulty: DifficultyLevel
    prompt: str
    order_index: int


class EngineAnswerRead(BaseModel):
    """Stored answer summary."""

    id: str
    question_id: str
    transcript: str
    duration_seconds: int | None
    submitted_at: datetime


class EngineSession(BaseModel):
    """Interview engine session state."""

    id: str
    role: str
    difficulty: DifficultyLevel
    duration_minutes: int
    categories: list[EngineQuestionCategory]
    status: InterviewStatus
    timer: EngineTimer
    total_questions: int
    answered_questions: int
    current_question: EngineQuestion | None


class StartInterviewResponse(EngineSession):
    """Start-session response."""

    generated_questions: list[EngineQuestion]


class SubmitAnswerRequest(BaseModel):
    """Request body for submitting the current answer."""

    answer: str = Field(..., min_length=1, max_length=20000)
    question_id: str | None = None
    duration_seconds: int | None = Field(default=None, ge=0)


class SubmitAnswerResponse(BaseModel):
    """Answer submission response."""

    session: EngineSession
    stored_answer: EngineAnswerRead
    next_question: EngineQuestion | None


class CompleteInterviewResponse(BaseModel):
    """Completed interview response."""

    session: EngineSession
    answers: list[EngineAnswerRead]


class SupportedEngineOptions(BaseModel):
    """Supported engine option metadata."""

    roles_note: str
    difficulties: list[DifficultyLevel]
    categories: list[EngineQuestionCategory]
    duration_minutes: dict[str, int]
