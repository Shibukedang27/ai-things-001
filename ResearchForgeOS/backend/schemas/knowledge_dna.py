from datetime import datetime
from typing import Any

from pydantic import Field

from backend.schemas.common import APIModel, TimestampedRead


class KnowledgeNodeRead(TimestampedRead):
    id: str
    stable_key: str
    node_type: str
    name: str
    label: str
    description: str | None
    importance_score: float
    metadata_json: dict[str, Any]


class KnowledgeEdgeRead(TimestampedRead):
    id: str
    source_node_id: str | None
    target_node_id: str | None
    source_key: str
    target_key: str
    edge_type: str
    weight: float
    confidence_score: float
    description: str
    metadata_json: dict[str, Any]


class KnowledgeHierarchyRead(TimestampedRead):
    id: str
    parent_topic: str
    child_topic: str
    hierarchy_type: str
    confidence_score: float
    evidence: str


class LearningPathRead(TimestampedRead):
    id: str
    order_index: int
    topic: str
    reason: str
    estimated_hours: int
    difficulty_level: str
    resource_hint: str


class PrerequisiteRead(TimestampedRead):
    id: str
    topic: str
    prerequisite_type: str
    importance_score: float
    source_concept: str | None


class RelatedDocumentRead(TimestampedRead):
    id: str
    related_document_id: str
    title: str
    similarity_score: float
    shared_signals: list[str]
    relationship_reason: str


class KnowledgeDNARead(TimestampedRead):
    id: str
    document_id: str
    document_title: str
    difficulty_level: str
    estimated_reading_time_minutes: int
    knowledge_score: float
    interview_importance: float
    industry_relevance: float
    implementation_complexity: float
    research_category: str
    primary_concepts: list[str]
    secondary_concepts: list[str]
    prerequisites: list[str]
    advanced_topics: list[str]
    future_learning_topics: list[str]
    technologies_used: list[str]
    programming_languages: list[str]
    frameworks: list[str]
    libraries: list[str]
    algorithms: list[str]
    datasets: list[str]
    research_papers: list[str]
    learning_order: list[str]
    estimated_mastery_time_hours: int
    mathematical_topics: list[str]
    parent_topics: list[str]
    child_topics: list[str]
    sibling_topics: list[str]
    knowledge_chains: list[list[str]]
    research_evolution: list[str]
    metadata_json: dict[str, Any]
    nodes: list[KnowledgeNodeRead] = Field(default_factory=list)
    edges: list[KnowledgeEdgeRead] = Field(default_factory=list)
    hierarchy_items: list[KnowledgeHierarchyRead] = Field(default_factory=list)
    learning_path_steps: list[LearningPathRead] = Field(default_factory=list)
    prerequisite_items: list[PrerequisiteRead] = Field(default_factory=list)
    related_documents: list[RelatedDocumentRead] = Field(default_factory=list)


class KnowledgeDNAUpdate(APIModel):
    interview_importance: float | None = Field(default=None, ge=0, le=1)
    industry_relevance: float | None = Field(default=None, ge=0, le=1)
    implementation_complexity: float | None = Field(default=None, ge=0, le=1)
    research_category: str | None = Field(default=None, min_length=2, max_length=120)
    primary_concepts: list[str] | None = None
    secondary_concepts: list[str] | None = None
    prerequisites: list[str] | None = None
    advanced_topics: list[str] | None = None
    future_learning_topics: list[str] | None = None
    learning_order: list[str] | None = None
    estimated_mastery_time_hours: int | None = Field(default=None, ge=1)


class RelatedTopicRead(APIModel):
    topic: str
    relationship_type: str
    confidence_score: float
    source: str


class KnowledgeDNAStats(APIModel):
    document_id: str
    dna_id: str
    generated_at: datetime
    node_count: int
    edge_count: int
    prerequisite_count: int
    learning_path_steps: int
