from __future__ import annotations

from datetime import datetime
from typing import Any

from adaptive_learning.types import CardDifficulty, ReviewRating, RevisionPlanType
from pydantic import Field

from backend.schemas.common import APIModel, TimestampedRead


class FlashcardRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    document_id: str
    card_type: str
    difficulty: str
    front: str
    back: str
    explanation: str
    tags: list[str]
    source_excerpt: str
    active: bool
    metadata_json: dict[str, Any]


class QuizQuestionRead(TimestampedRead):
    id: str
    quiz_id: str
    order_index: int
    question_type: str
    prompt: str
    choices: list[str]
    correct_answers: list[str]
    explanation: str
    difficulty: str
    points: int
    metadata_json: dict[str, Any]


class QuizRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    document_id: str
    title: str
    quiz_type: str
    difficulty: str
    time_limit_seconds: int
    adaptive: bool
    status: str
    metadata_json: dict[str, Any]
    questions: list[QuizQuestionRead] = Field(default_factory=list)


class QuizAttemptRead(TimestampedRead):
    id: str
    quiz_id: str
    owner_user_id: str | None
    status: str
    started_at: datetime
    submitted_at: datetime | None
    time_spent_seconds: int
    answers: dict[str, Any]
    score: float
    total_points: float
    accuracy: float
    passed: bool
    feedback: list[dict[str, Any]]
    metadata_json: dict[str, Any]


class StartQuizResponse(APIModel):
    attempt: QuizAttemptRead
    quiz: QuizRead


class SubmitQuizRequest(APIModel):
    answers: dict[str, Any] = Field(default_factory=dict)
    time_spent_seconds: int = Field(default=0, ge=0, le=86_400)


class SubmitQuizResponse(APIModel):
    attempt: QuizAttemptRead
    progress: ProgressRead
    achievements: list[AchievementRead]
    certificate: CertificateRead | None = None


class ReviewFlashcardItem(APIModel):
    flashcard_id: str
    rating: ReviewRating
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    response_quality: float = Field(default=0.7, ge=0.0, le=1.0)
    duration_ms: int = Field(default=0, ge=0, le=3_600_000)


class ReviewFlashcardsRequest(APIModel):
    reviews: list[ReviewFlashcardItem] = Field(min_length=1, max_length=100)


class ReviewRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    flashcard_id: str
    rating: str
    response_quality: float
    correct: bool
    confidence: float
    reviewed_at: datetime
    scheduled_before: datetime | None
    next_review_at: datetime | None
    memory_strength: float
    retention_score: float
    duration_ms: int
    metadata_json: dict[str, Any]


class MemoryTrackingRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    document_id: str | None
    flashcard_id: str | None
    concept: str
    memory_strength: float
    confidence: float
    retention_score: float
    review_count: int
    success_rate: float
    last_review_at: datetime | None
    next_review_at: datetime | None
    forgetting_curve: list[dict[str, Any]]
    mastery_percentage: float
    metadata_json: dict[str, Any]


class ReviewFlashcardsResponse(APIModel):
    reviews: list[ReviewRead]
    memory: list[MemoryTrackingRead]
    progress: ProgressRead
    achievements: list[AchievementRead]


class LearningSessionRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    document_id: str | None
    session_type: str
    title: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: int
    items_studied: int
    correct_count: int
    total_count: int
    mastery_delta: float
    metadata_json: dict[str, Any]


class AchievementRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    achievement_type: str
    title: str
    description: str
    badge: str
    skill_level: str
    points: int
    awarded_at: datetime
    metadata_json: dict[str, Any]


class CertificateRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    document_id: str | None
    title: str
    certificate_type: str
    issued_at: datetime
    score: float
    mastery_percentage: float
    verification_code: str
    metadata_json: dict[str, Any]


class ProgressRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    document_id: str | None
    knowledge_score: float
    retention_score: float
    weak_concepts: list[str]
    strong_concepts: list[str]
    learning_velocity: float
    quiz_accuracy: float
    memory_heatmap: dict[str, Any]
    study_time_minutes: int
    completion_rate: float
    mastery_graph: list[dict[str, Any]]
    mastered_items: int
    total_items: int
    streak_days: int
    last_activity_at: datetime | None
    metadata_json: dict[str, Any]


class CodingChallengeRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    document_id: str
    title: str
    difficulty: str
    prompt: str
    starter_code: str
    hints: list[str]
    optimal_solution: str
    complexity_analysis: str
    alternative_solutions: list[str]
    edge_cases: list[str]
    unit_tests: list[dict[str, Any]]
    tags: list[str]
    status: str
    metadata_json: dict[str, Any]


class RevisionPlanRead(TimestampedRead):
    id: str
    owner_user_id: str | None
    document_id: str
    plan_type: str
    title: str
    schedule: list[dict[str, Any]]
    focus_concepts: list[str]
    estimated_minutes: int
    status: str
    due_at: datetime | None
    metadata_json: dict[str, Any]


class GenerateLearningRequest(APIModel):
    force: bool = False


class GenerateQuizRequest(APIModel):
    difficulty: CardDifficulty | None = None
    question_limit: int = Field(default=14, ge=1, le=50)


class GenerateRevisionPlanRequest(APIModel):
    plan_type: RevisionPlanType = RevisionPlanType.DAILY


class LearningBundleRead(APIModel):
    document_id: str
    flashcards: list[FlashcardRead]
    quiz: QuizRead
    interview_questions: list[dict[str, Any]]
    coding_challenges: list[CodingChallengeRead]
    revision_plans: list[RevisionPlanRead]
    progress: ProgressRead
    achievements: list[AchievementRead]


class LearningProgressResponse(APIModel):
    progress: list[ProgressRead]


SubmitQuizResponse.model_rebuild()
ReviewFlashcardsResponse.model_rebuild()
