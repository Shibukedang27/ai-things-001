"""AI evaluation API schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class EvaluationScoreBreakdown(BaseModel):
    """Score dimensions for one answer evaluation."""

    technical_accuracy: Decimal = Field(..., ge=0, le=100)
    communication: Decimal = Field(..., ge=0, le=100)
    completeness: Decimal = Field(..., ge=0, le=100)
    confidence_score: Decimal = Field(..., ge=0, le=100)
    problem_solving: Decimal = Field(..., ge=0, le=100)
    explanation_quality: Decimal = Field(..., ge=0, le=100)
    overall_score: Decimal = Field(..., ge=0, le=100)


class EvaluationContent(BaseModel):
    """Generated answer guidance."""

    correct_answer: str
    better_answer: str
    industry_standard_answer: str
    improvement_suggestions: list[str]
    related_topics: list[str]
    difficulty_analysis: dict[str, Any]


class AnswerEvaluationRead(ORMModel):
    """Persisted answer evaluation response."""

    id: str
    user_id: str
    interview_id: str
    question_id: str
    answer_id: str
    technical_accuracy: Decimal
    communication: Decimal
    completeness: Decimal
    confidence_score: Decimal
    problem_solving: Decimal
    explanation_quality: Decimal
    overall_score: Decimal
    correct_answer: str
    better_answer: str
    industry_standard_answer: str
    improvement_suggestions: list[str]
    related_topics: list[str]
    difficulty_analysis: dict[str, Any]
    evaluator_version: str
    created_at: datetime
    updated_at: datetime


class EvaluateAnswerResponse(BaseModel):
    """Single-answer evaluation response."""

    evaluation: AnswerEvaluationRead


class EvaluateInterviewResponse(BaseModel):
    """Bulk interview evaluation response."""

    interview_id: str
    evaluated_count: int
    skipped_count: int
    evaluations: list[AnswerEvaluationRead]


class EvaluationOptions(BaseModel):
    """Evaluation engine metadata."""

    dimensions: list[str]
    generated_outputs: list[str]
    evaluator_version: str
