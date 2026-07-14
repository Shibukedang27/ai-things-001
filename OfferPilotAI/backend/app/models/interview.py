"""Interview product ORM models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.domain.enums import (
    DifficultyLevel,
    InterviewHistoryEvent,
    InterviewStatus,
    InterviewType,
    LeaderboardPeriod,
    QuestionCategory,
    ReportStatus,
    RoadmapStatus,
    SeniorityLevel,
    SessionStatus,
)
from app.utils.ids import create_id


class Interview(TimestampMixin, Base):
    """A candidate's interview practice session or scheduled interview."""

    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    role_title: Mapped[str] = mapped_column(String(160), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    seniority: Mapped[str] = mapped_column(String(32), nullable=False, default=SeniorityLevel.MID.value, server_default=SeniorityLevel.MID.value)
    interview_type: Mapped[str] = mapped_column(String(32), nullable=False, default=InterviewType.MIXED.value, server_default=InterviewType.MIXED.value)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=InterviewStatus.DRAFT.value, server_default=InterviewStatus.DRAFT.value, index=True)
    focus_areas: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=45, server_default="45")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))

    user: Mapped["User"] = relationship(back_populates="interviews")
    questions: Mapped[list["Question"]] = relationship(back_populates="interview", cascade="all, delete-orphan")
    answers: Mapped[list["Answer"]] = relationship(back_populates="interview", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="interview", cascade="all, delete-orphan")
    history: Mapped[list["InterviewHistory"]] = relationship(back_populates="interview", cascade="all, delete-orphan")


class Question(TimestampMixin, Base):
    """Question catalog item or interview-specific prompt."""

    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    interview_id: Mapped[str | None] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    category: Mapped[str] = mapped_column(String(32), nullable=False, default=QuestionCategory.BEHAVIORAL.value, server_default=QuestionCategory.BEHAVIORAL.value)
    difficulty: Mapped[str] = mapped_column(String(32), nullable=False, default=DifficultyLevel.MEDIUM.value, server_default=DifficultyLevel.MEDIUM.value)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    expected_signal: Mapped[str | None] = mapped_column(String(80), nullable=True)
    rubric: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"), index=True)

    interview: Mapped["Interview | None"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class Answer(TimestampMixin, Base):
    """Candidate answer for an interview question."""

    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    feedback: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))

    user: Mapped["User"] = relationship(back_populates="answers")
    interview: Mapped["Interview"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship(back_populates="answers")


class Report(TimestampMixin, Base):
    """Generated interview performance report."""

    __tablename__ = "reports"
    __table_args__ = (UniqueConstraint("interview_id", "version", name="uq_reports_interview_id_version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=ReportStatus.DRAFT.value, server_default=ReportStatus.DRAFT.value, index=True)
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    strengths: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    improvement_areas: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    recommendations: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")

    user: Mapped["User"] = relationship(back_populates="reports")
    interview: Mapped["Interview"] = relationship(back_populates="reports")
    learning_roadmaps: Mapped[list["LearningRoadmap"]] = relationship(back_populates="report")


class LearningRoadmap(TimestampMixin, Base):
    """Personalized learning roadmap generated from interview performance."""

    __tablename__ = "learning_roadmaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    report_id: Mapped[str | None] = mapped_column(ForeignKey("reports.id", ondelete="SET NULL"), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    target_role: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=RoadmapStatus.DRAFT.value, server_default=RoadmapStatus.DRAFT.value, index=True)
    estimated_weeks: Mapped[int] = mapped_column(Integer, nullable=False, default=4, server_default="4")
    recommended_topics: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    milestones: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    weak_topics: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    leetcode_problems: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    hackerrank_problems: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    books: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    courses: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    youtube_videos: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    daily_practice_plan: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    weekly_roadmap: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    monthly_roadmap: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    source_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))

    user: Mapped["User"] = relationship(back_populates="learning_roadmaps")
    report: Mapped["Report | None"] = relationship(back_populates="learning_roadmaps")


class Leaderboard(TimestampMixin, Base):
    """Leaderboard entry for candidate progress tracking."""

    __tablename__ = "leaderboard"
    __table_args__ = (
        UniqueConstraint("period", "user_id", name="uq_leaderboard_period_user_id"),
        UniqueConstraint("period", "rank", name="uq_leaderboard_period_rank"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    period: Mapped[str] = mapped_column(String(32), nullable=False, default=LeaderboardPeriod.WEEKLY.value, server_default=LeaderboardPeriod.WEEKLY.value, index=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=0, server_default="0")
    percentile: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    interviews_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    user: Mapped["User"] = relationship(back_populates="leaderboard_entries")


class Session(TimestampMixin, Base):
    """Authenticated user session."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_jti: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=SessionStatus.ACTIVE.value, server_default=SessionStatus.ACTIVE.value, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")


class InterviewHistory(TimestampMixin, Base):
    """Append-only audit history for interview lifecycle events."""

    __tablename__ = "interview_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=create_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, default=InterviewHistoryEvent.CREATED.value, server_default=InterviewHistoryEvent.CREATED.value, index=True)
    event_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="interview_history")
    interview: Mapped["Interview"] = relationship(back_populates="history")


# Backward-compatible aliases for earlier backend foundation names.
InterviewSession = Interview
InterviewQuestion = Question
InterviewAnswer = Answer
