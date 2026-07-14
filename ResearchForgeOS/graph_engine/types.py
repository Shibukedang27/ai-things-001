from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class GraphNodeType(StrEnum):
    DOCUMENT = "document"
    RESEARCH_PAPER = "research_paper"
    BOOK = "book"
    CONCEPT = "concept"
    ALGORITHM = "algorithm"
    TECHNOLOGY = "technology"
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATASET = "dataset"
    AUTHOR = "author"
    COMPANY = "company"
    UNIVERSITY = "university"
    COURSE = "course"
    PROJECT = "project"
    INTERVIEW_TOPIC = "interview_topic"
    TOOL = "tool"
    MODEL = "model"
    API = "api"


class GraphRelationshipType(StrEnum):
    USES = "uses"
    IMPLEMENTS = "implements"
    INSPIRED_BY = "inspired_by"
    DEPENDS_ON = "depends_on"
    REQUIRES = "requires"
    IMPROVES = "improves"
    INTRODUCED_BY = "introduced_by"
    RELATED_TO = "related_to"
    ALTERNATIVE_TO = "alternative_to"
    BUILT_WITH = "built_with"
    PREREQUISITE = "prerequisite"
    PARENT_TOPIC = "parent_topic"
    CHILD_TOPIC = "child_topic"
    REFERENCED_BY = "referenced_by"
    EXPLAINS = "explains"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"


@dataclass(frozen=True)
class GraphConceptInput:
    id: str | None
    name: str
    concept_type: str
    description: str
    prerequisites: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    difficulty_level: str = "intermediate"
    confidence_score: float = 0.7


@dataclass(frozen=True)
class GraphTechnologyInput:
    id: str | None
    name: str
    category: str
    confidence_score: float = 0.7
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GraphReferenceInput:
    title: str | None
    authors: list[str]
    year: int | None
    source: str | None
    url: str | None
    citation_text: str
    reference_type: str
    confidence_score: float


@dataclass(frozen=True)
class GraphRelationshipInput:
    source_name: str
    target_name: str
    relationship_type: str
    description: str
    confidence_score: float


@dataclass(frozen=True)
class GraphDNAInput:
    research_category: str | None = None
    knowledge_score: float = 0.5
    primary_concepts: list[str] = field(default_factory=list)
    secondary_concepts: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    advanced_topics: list[str] = field(default_factory=list)
    future_learning_topics: list[str] = field(default_factory=list)
    technologies_used: list[str] = field(default_factory=list)
    programming_languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    libraries: list[str] = field(default_factory=list)
    algorithms: list[str] = field(default_factory=list)
    datasets: list[str] = field(default_factory=list)
    research_papers: list[str] = field(default_factory=list)
    learning_order: list[str] = field(default_factory=list)
    mathematical_topics: list[str] = field(default_factory=list)
    parent_topics: list[str] = field(default_factory=list)
    child_topics: list[str] = field(default_factory=list)
    sibling_topics: list[str] = field(default_factory=list)
    research_evolution: list[str] = field(default_factory=list)
    related_documents: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class GraphDocumentInput:
    id: str
    title: str
    author: str | None
    category: str
    source_type: str
    difficulty: str
    created_at: str | None
    topics: list[str]
    keywords: list[str]
    technologies: list[GraphTechnologyInput]
    concepts: list[GraphConceptInput]
    algorithms: list[str]
    references: list[GraphReferenceInput]
    relationships: list[GraphRelationshipInput]
    cleaned_text: str
    dna: GraphDNAInput | None = None


@dataclass(frozen=True)
class GraphBuildInput:
    document: GraphDocumentInput
    existing_nodes: list[dict[str, Any]] = field(default_factory=list)
    existing_edges: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class GraphNodeDraft:
    stable_key: str
    node_type: str
    name: str
    label: str
    description: str
    importance_score: float
    confidence_score: float
    size: float
    color: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdgeDraft:
    stable_key: str
    source_key: str
    target_key: str
    relationship_type: str
    label: str
    description: str
    weight: float
    confidence_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphLayoutItem:
    stable_key: str
    x: float
    y: float


@dataclass(frozen=True)
class GraphBuildResult:
    nodes: list[GraphNodeDraft]
    edges: list[GraphEdgeDraft]
    layout: list[GraphLayoutItem]
    analytics: dict[str, Any]
    insights: dict[str, Any]
    interaction: dict[str, Any]
