from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class NoteType(StrEnum):
    SMART_NOTE = "smart_note"
    SCRATCHPAD = "scratchpad"
    DAILY_NOTE = "daily_note"
    CANVAS_NOTE = "canvas_note"
    AI_RESPONSE = "ai_response"
    CODE_SNIPPET = "code_snippet"
    RESEARCH_NOTE = "research_note"


class WritingMode(StrEnum):
    REWRITE = "rewrite"
    EXPAND = "expand"
    SIMPLIFY = "simplify"
    PROFESSIONAL = "professional_tone"
    ACADEMIC = "academic_tone"
    ELI5 = "explain_like_im_five"
    TECHNICAL = "technical_explanation"
    GRAMMAR = "grammar_improvement"
    CITATION = "citation_generator"
    MARKDOWN = "markdown_formatter"


class SearchMode(StrEnum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    FUZZY = "fuzzy"
    TAG = "tag"
    DATE = "date"
    PROJECT = "project"
    AUTHOR = "author"
    CONCEPT = "concept"
    HYBRID = "hybrid"


class ChecklistType(StrEnum):
    RESEARCH = "research_checklist"
    LEARNING = "learning_checklist"
    IMPLEMENTATION = "implementation_checklist"
    READING = "reading_plan"
    CODING = "coding_plan"
    REVISION = "revision_plan"


@dataclass(frozen=True)
class NoteAnalysis:
    title: str
    summary: str
    keywords: list[str]
    tags: list[str]
    concepts: list[str]
    category: str
    action_items: list[str]
    duplicate_key: str
    content_hash: str
    confidence_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchableNote:
    id: str
    title: str
    content: str
    summary: str
    tags: list[str]
    keywords: list[str]
    concepts: list[str]
    category: str
    author: str | None
    project_id: str | None
    collection_id: str | None
    created_at: datetime | None
    updated_at: datetime | None
    embedding: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NoteSearchResult:
    note_id: str
    title: str
    summary: str
    score: float
    matched_fields: list[str]
    tags: list[str]
    concepts: list[str]
    project_id: str | None
    collection_id: str | None


@dataclass(frozen=True)
class WritingResult:
    mode: WritingMode
    original_text: str
    output_text: str
    changes: list[str]
    citations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskPlan:
    plan_type: ChecklistType
    title: str
    overview: str
    checklist: list[dict[str, object]]
    estimated_days: int
    milestones: list[str]
    resources: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
