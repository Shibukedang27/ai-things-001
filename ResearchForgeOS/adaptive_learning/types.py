from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class CardType(StrEnum):
    DEFINITION = "definition"
    CONCEPT = "concept"
    FORMULA = "formula"
    ALGORITHM = "algorithm"
    CODE = "code"
    INTERVIEW = "interview"
    TRUE_FALSE = "true_false"
    IMAGE_PLACEHOLDER = "image_placeholder"
    FILL_BLANK = "fill_in_blank"
    REVERSE = "reverse"


class CardDifficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuizQuestionType(StrEnum):
    MCQ = "mcq"
    MULTIPLE_CORRECT = "multiple_correct"
    FILL_BLANK = "fill_in_blank"
    CODE_COMPLETION = "code_completion"
    SCENARIO = "scenario"
    CASE_STUDY = "case_study"
    RESEARCH = "research"
    DEBUGGING = "debugging"
    ALGORITHM = "algorithm"


class InterviewQuestionType(StrEnum):
    HR = "hr"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    MACHINE_LEARNING = "machine_learning"
    SYSTEM_DESIGN = "system_design"
    PYTHON = "python"
    JAVA = "java"
    SQL = "sql"
    BACKEND = "backend"
    NLP = "nlp"
    GENERATIVE_AI = "generative_ai"
    PROMPT_ENGINEERING = "prompt_engineering"
    FOLLOW_UP = "follow_up"


class ReviewRating(StrEnum):
    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"


class RevisionPlanType(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUICK = "quick"
    EXAM = "exam"
    INTERVIEW = "interview"
    CODING = "coding"


@dataclass(frozen=True)
class LearningConcept:
    name: str
    description: str
    difficulty: CardDifficulty
    keywords: list[str] = field(default_factory=list)
    source_excerpt: str = ""


@dataclass(frozen=True)
class LearningSource:
    document_id: str
    title: str
    category: str
    difficulty: str
    topics: list[str]
    concepts: list[LearningConcept]
    keywords: list[str]
    technologies: list[str]
    definitions: list[dict[str, str]]
    algorithms: list[dict[str, str]]
    equations: list[dict[str, str]]
    code_snippets: list[dict[str, str]]
    summaries: dict[str, str]
    learning_objectives: list[str]
    cleaned_text: str


@dataclass(frozen=True)
class FlashcardDraft:
    card_type: CardType
    difficulty: CardDifficulty
    front: str
    back: str
    explanation: str
    tags: list[str]
    source_excerpt: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QuizQuestionDraft:
    question_type: QuizQuestionType
    prompt: str
    choices: list[str]
    correct_answers: list[str]
    explanation: str
    difficulty: CardDifficulty
    points: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QuizDraft:
    title: str
    quiz_type: str
    difficulty: CardDifficulty
    time_limit_seconds: int
    adaptive: bool
    questions: list[QuizQuestionDraft]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InterviewQuestionDraft:
    question_type: InterviewQuestionType
    difficulty: CardDifficulty
    question: str
    ideal_answer: str
    follow_ups: list[str]
    evaluation_points: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CodingChallengeDraft:
    difficulty: CardDifficulty
    title: str
    prompt: str
    starter_code: str
    hints: list[str]
    optimal_solution: str
    complexity_analysis: str
    alternative_solutions: list[str]
    edge_cases: list[str]
    unit_tests: list[dict[str, Any]]
    tags: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RevisionPlanDraft:
    plan_type: RevisionPlanType
    title: str
    schedule: list[dict[str, Any]]
    focus_concepts: list[str]
    estimated_minutes: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryState:
    memory_strength: float
    confidence: float
    retention_score: float
    review_count: int
    success_rate: float
    last_review_at: datetime | None
    next_review_at: datetime | None
    forgetting_curve: list[dict[str, Any]]
    mastery_percentage: float


@dataclass(frozen=True)
class LearningAnalytics:
    knowledge_score: float
    retention_score: float
    weak_concepts: list[str]
    strong_concepts: list[str]
    learning_velocity: float
    quiz_accuracy: float
    memory_heatmap: dict[str, float]
    study_time_minutes: int
    completion_rate: float
    mastery_graph: list[dict[str, Any]]


@dataclass(frozen=True)
class AchievementDraft:
    achievement_type: str
    title: str
    description: str
    badge: str
    skill_level: str
    points: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AdaptiveLearningBundle:
    flashcards: list[FlashcardDraft]
    quiz: QuizDraft
    interview_questions: list[InterviewQuestionDraft]
    coding_challenges: list[CodingChallengeDraft]
    revision_plans: list[RevisionPlanDraft]
    analytics: LearningAnalytics
    achievements: list[AchievementDraft]
