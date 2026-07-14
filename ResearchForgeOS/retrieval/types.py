from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class QueryIntent(StrEnum):
    QUESTION = "question"
    COMPARISON = "comparison"
    IMPLEMENTATION_REQUEST = "implementation_request"
    DEFINITION = "definition"
    RESEARCH_REQUEST = "research_request"
    CODING_HELP = "coding_help"
    INTERVIEW_QUESTION = "interview_question"
    SUMMARY_REQUEST = "summary_request"
    ROADMAP_REQUEST = "roadmap_request"


class SearchMode(StrEnum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class QueryProfile:
    original_query: str
    sanitized_query: str
    normalized_query: str
    intent: QueryIntent
    expanded_queries: list[str]
    keywords: list[str]
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchOptions:
    top_k: int = 8
    namespace: str = "researchforge"
    collection_name: str = "knowledge"
    filters: dict[str, Any] = field(default_factory=dict)
    max_context_characters: int = 1200


@dataclass(frozen=True)
class KnowledgeSection:
    section_id: str
    document_id: str
    document_title: str
    content: str
    section_label: str
    chunk_id: str | None = None
    source_type: str | None = None
    source_url: str | None = None
    category: str | None = None
    topics: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalCandidate:
    section: KnowledgeSection
    score: float
    keyword_score: float
    semantic_score: float
    metadata_score: float
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Citation:
    citation_key: str
    document_id: str
    document_title: str
    snippet: str
    relevance_score: float
    chunk_id: str | None = None
    source_url: str | None = None
    section_label: str | None = None


@dataclass(frozen=True)
class ReasoningStep:
    step_index: int
    step_type: str
    description: str
    evidence: list[str]
    confidence_score: float


@dataclass(frozen=True)
class ReasonedAnswer:
    answer: str
    confidence_score: float
    citations: list[Citation]
    retrieved_sections: list[RetrievalCandidate]
    reasoning_path: list[ReasoningStep]
    supporting_evidence: list[str]
    validation: dict[str, Any]
    cache_key: str
    cache_hit: bool = False
