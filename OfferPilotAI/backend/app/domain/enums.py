"""Shared domain enums."""

from enum import StrEnum


class InterviewType(StrEnum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    CASE_STUDY = "case_study"
    LEADERSHIP = "leadership"
    MIXED = "mixed"


class SeniorityLevel(StrEnum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    EXECUTIVE = "executive"


class InterviewSessionStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewStatus(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class DifficultyLevel(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class CodingLanguage(StrEnum):
    PYTHON = "python"
    JAVA = "java"
    SQL = "sql"


class CodeRunStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNSUPPORTED = "unsupported"
    SKIPPED = "skipped"


class QuestionCategory(StrEnum):
    BACKGROUND = "background"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    PRODUCT = "product"
    LEADERSHIP = "leadership"
    CULTURE = "culture"


class EvaluationSignal(StrEnum):
    CLARITY = "clarity"
    STRUCTURE = "structure"
    CORRECTNESS = "correctness"
    DEPTH = "depth"
    COMMUNICATION = "communication"
    CONFIDENCE = "confidence"


class ReportStatus(StrEnum):
    DRAFT = "draft"
    GENERATED = "generated"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class RoadmapStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class LeaderboardPeriod(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


class SessionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class InterviewHistoryEvent(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    STARTED = "started"
    ANSWER_SUBMITTED = "answer_submitted"
    COMPLETED = "completed"
    REPORT_GENERATED = "report_generated"
