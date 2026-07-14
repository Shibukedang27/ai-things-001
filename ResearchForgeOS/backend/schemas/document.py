from datetime import datetime
from typing import Any

from pydantic import Field, HttpUrl

from backend.schemas.common import APIModel, TimestampedRead


class DocumentChunkRead(TimestampedRead):
    id: str
    chunk_index: int
    content: str
    token_count: int
    character_count: int
    start_char: int
    end_char: int
    content_hash: str
    metadata_json: dict[str, Any]


class DocumentSummaryRead(TimestampedRead):
    id: str
    summary_type: str
    content: str
    word_count: int
    confidence_score: float


class DocumentConceptRead(TimestampedRead):
    id: str
    name: str
    normalized_name: str
    concept_type: str
    description: str
    prerequisites: list[str]
    dependencies: list[str]
    difficulty_level: str
    confidence_score: float


class DocumentKeywordRead(TimestampedRead):
    id: str
    value: str
    normalized_value: str
    relevance_score: float
    occurrence_count: int


class DocumentTechnologyRead(TimestampedRead):
    id: str
    name: str
    normalized_name: str
    category: str
    confidence_score: float
    evidence: list[str]


class DocumentEmbeddingMetadataRead(TimestampedRead):
    id: str
    chunk_id: str | None
    embedding_model: str
    embedding_dimensions: int
    content_hash: str
    metadata_json: dict[str, Any]


class DocumentReferenceRead(TimestampedRead):
    id: str
    title: str | None
    authors: list[str]
    year: int | None
    source: str | None
    url: str | None
    citation_text: str
    reference_type: str
    confidence_score: float


class KnowledgeRelationshipRead(TimestampedRead):
    id: str
    source_entity_type: str
    source_entity_id: str | None
    source_name: str
    target_entity_type: str
    target_entity_id: str | None
    target_name: str
    relationship_type: str
    description: str
    confidence_score: float
    metadata_json: dict[str, Any]


class DocumentListItem(TimestampedRead):
    id: str
    title: str
    author: str | None
    category: str
    source_type: str
    status: str
    difficulty: str
    estimated_reading_time_minutes: int
    word_count: int
    topics: list[str]


class DocumentRead(DocumentListItem):
    original_filename: str | None
    mime_type: str | None
    source_url: str | None
    language: str
    character_count: int
    content_hash: str
    definitions: list[dict[str, str]]
    algorithms: list[dict[str, str]]
    equations: list[dict[str, str]]
    code_snippets: list[dict[str, str]]
    learning_objectives: list[str]
    learning_assets: dict[str, Any]
    metadata_json: dict[str, Any]
    summaries: list[DocumentSummaryRead] = Field(default_factory=list)
    concepts: list[DocumentConceptRead] = Field(default_factory=list)
    keywords: list[DocumentKeywordRead] = Field(default_factory=list)
    technologies: list[DocumentTechnologyRead] = Field(default_factory=list)
    embeddings: list[DocumentEmbeddingMetadataRead] = Field(default_factory=list)
    references: list[DocumentReferenceRead] = Field(default_factory=list)
    relationships: list[KnowledgeRelationshipRead] = Field(default_factory=list)


class DocumentMetadataRead(APIModel):
    id: str
    title: str
    author: str | None
    category: str
    topics: list[str]
    keywords: list[str]
    technologies: list[str]
    difficulty: str
    estimated_reading_time_minutes: int
    word_count: int
    character_count: int
    language: str
    source_type: str
    content_hash: str
    learning_objectives: list[str]
    definitions_count: int
    algorithms_count: int
    equations_count: int
    code_snippets_count: int
    references_count: int
    concepts_count: int
    created_at: datetime
    updated_at: datetime


class DocumentUploadForm(APIModel):
    title: str | None = Field(default=None, max_length=240)
    author: str | None = Field(default=None, max_length=160)
    category: str | None = Field(default=None, max_length=120)
    source_type: str | None = Field(default=None, max_length=60)
    source_url: HttpUrl | None = None
    source_text: str | None = Field(default=None, min_length=10)
