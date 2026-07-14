from datetime import datetime
from typing import Any

from pydantic import Field

from backend.schemas.common import APIModel, TimestampedRead


class RetrievalRequest(APIModel):
    query: str = Field(min_length=2, max_length=4000)
    top_k: int = Field(default=8, ge=1, le=50)
    namespace: str = Field(default="researchforge", min_length=3, max_length=120)
    collection_name: str = Field(default="knowledge", min_length=3, max_length=120)
    filters: dict[str, Any] = Field(default_factory=dict)
    max_context_characters: int = Field(default=1200, ge=240, le=8000)


class AskQuestionRequest(RetrievalRequest):
    include_reasoning: bool = True
    use_cache: bool = True


class RetrievedSectionRead(APIModel):
    document_id: str
    document_title: str
    chunk_id: str | None
    section_label: str
    content: str
    score: float
    keyword_score: float
    semantic_score: float
    metadata_score: float
    reasons: list[str]
    source_type: str | None
    source_url: str | None
    topics: list[str]
    keywords: list[str]
    technologies: list[str]


class CitationRead(APIModel):
    citation_key: str
    document_id: str | None
    document_title: str
    chunk_id: str | None
    snippet: str
    source_url: str | None
    section_label: str | None
    relevance_score: float


class ReasoningStepRead(APIModel):
    step_index: int
    step_type: str
    description: str
    evidence: list[str]
    confidence_score: float


class RetrievalAnswerRead(APIModel):
    query_id: str
    history_id: str
    intent: str
    answer: str
    confidence_score: float
    source_documents: list[dict[str, Any]]
    citations: list[CitationRead]
    retrieved_sections: list[RetrievedSectionRead]
    reasoning_path: list[ReasoningStepRead]
    supporting_evidence: list[str]
    validation: dict[str, Any]
    cache_hit: bool


class SearchResponse(APIModel):
    query_id: str
    history_id: str
    mode: str
    intent: str
    results: list[RetrievedSectionRead]


class RelatedConceptRead(APIModel):
    concept: str
    document_ids: list[str]
    source_titles: list[str]
    relevance_score: float


class RelatedConceptsResponse(APIModel):
    query_id: str
    concepts: list[RelatedConceptRead]


class ReasoningHistoryItem(TimestampedRead):
    id: str
    query_id: str
    query_text: str
    intent: str
    mode: str
    status: str
    answer: str
    confidence_score: float
    cache_hit: bool
    source_documents: list[dict[str, Any]]


class CitationViewerResponse(APIModel):
    history_id: str
    citations: list[CitationRead]
    generated_at: datetime
