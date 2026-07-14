"""AI evaluation ORM models."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.utils.ids import create_id


class AnswerEvaluation(TimestampMixin, Base):
    """AI-generated evaluation for one answer."""

    __tablename__ = "answer_evaluations"
    __table_args__ = (UniqueConstraint("answer_id", name="uq_answer_evaluations_answer_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    answer_id: Mapped[str] = mapped_column(ForeignKey("answers.id", ondelete="CASCADE"), index=True, nullable=False)

    technical_accuracy: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    communication: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    completeness: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    problem_solving: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    explanation_quality: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    better_answer: Mapped[str] = mapped_column(Text, nullable=False)
    industry_standard_answer: Mapped[str] = mapped_column(Text, nullable=False)
    improvement_suggestions: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    related_topics: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    difficulty_analysis: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    evaluator_version: Mapped[str] = mapped_column(String(64), nullable=False, default="template-ai-v1")
