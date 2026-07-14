from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.document import Document
    from backend.models.user import User


class Flashcard(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "flashcards"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    card_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    source_excerpt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    active: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    document: Mapped[Document] = relationship("Document")
    reviews: Mapped[list[Review]] = relationship("Review", back_populates="flashcard", cascade="all, delete-orphan")
    memory_records: Mapped[list[MemoryTracking]] = relationship(
        "MemoryTracking",
        back_populates="flashcard",
        cascade="all, delete-orphan",
    )


class Quiz(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quizzes"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    quiz_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    adaptive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="active")
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    document: Mapped[Document] = relationship("Document")
    questions: Mapped[list[QuizQuestion]] = relationship(
        "QuizQuestion",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attempts: Mapped[list[QuizAttempt]] = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class QuizQuestion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quiz_questions"

    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    choices: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    correct_answers: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    quiz: Mapped[Quiz] = relationship("Quiz", back_populates="questions")


class QuizAttempt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quiz_attempts"

    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="started")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    answers: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_points: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    feedback: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    quiz: Mapped[Quiz] = relationship("Quiz", back_populates="attempts")
    owner: Mapped[User | None] = relationship("User")


class Review(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reviews"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    flashcard_id: Mapped[str] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"), index=True)
    rating: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    response_quality: Mapped[float] = mapped_column(Float, nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    scheduled_before: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    memory_strength: Mapped[float] = mapped_column(Float, nullable=False)
    retention_score: Mapped[float] = mapped_column(Float, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    flashcard: Mapped[Flashcard] = relationship("Flashcard", back_populates="reviews")


class LearningSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "learning_sessions"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    session_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_studied: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mastery_delta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    document: Mapped[Document | None] = relationship("Document")


class Achievement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "achievements"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "achievement_type", "title", name="uq_achievements_owner_type_title"),
    )

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    achievement_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    badge: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    skill_level: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")


class Certificate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "certificates"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    certificate_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    mastery_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    verification_code: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    document: Mapped[Document | None] = relationship("Document")


class MemoryTracking(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "memory_tracking"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "flashcard_id", name="uq_memory_tracking_owner_flashcard"),
    )

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    flashcard_id: Mapped[str | None] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"), index=True)
    concept: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    memory_strength: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    retention_score: Mapped[float] = mapped_column(Float, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, nullable=False)
    last_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    forgetting_curve: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    mastery_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    document: Mapped[Document | None] = relationship("Document")
    flashcard: Mapped[Flashcard | None] = relationship("Flashcard", back_populates="memory_records")


class Progress(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("owner_user_id", "document_id", name="uq_progress_owner_document"),)

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    knowledge_score: Mapped[float] = mapped_column(Float, nullable=False)
    retention_score: Mapped[float] = mapped_column(Float, nullable=False)
    weak_concepts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    strong_concepts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    learning_velocity: Mapped[float] = mapped_column(Float, nullable=False)
    quiz_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    memory_heatmap: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    study_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_rate: Mapped[float] = mapped_column(Float, nullable=False)
    mastery_graph: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    mastered_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    document: Mapped[Document | None] = relationship("Document")


class CodingChallenge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "coding_challenges"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    hints: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    optimal_solution: Mapped[str] = mapped_column(Text, nullable=False)
    complexity_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    alternative_solutions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    edge_cases: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    unit_tests: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="active")
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    document: Mapped[Document] = relationship("Document")


class RevisionPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "revision_plans"

    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    plan_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(220), index=True, nullable=False)
    schedule: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    focus_concepts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="active")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped[User | None] = relationship("User")
    document: Mapped[Document] = relationship("Document")
