from dataclasses import dataclass, field


@dataclass(frozen=True)
class DNAConceptInput:
    id: str | None
    name: str
    concept_type: str
    description: str
    prerequisites: list[str]
    dependencies: list[str]
    difficulty_level: str
    confidence_score: float


@dataclass(frozen=True)
class DNATechnologyInput:
    id: str | None
    name: str
    category: str
    confidence_score: float
    evidence: list[str]


@dataclass(frozen=True)
class RelatedDocumentCandidate:
    id: str
    title: str
    category: str
    topics: list[str]
    concepts: list[str]
    technologies: list[str]
    similarity_score: float = 0.0
    shared_signals: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DNADocumentInput:
    id: str
    title: str
    category: str
    difficulty: str
    estimated_reading_time_minutes: int
    word_count: int
    topics: list[str]
    keywords: list[str]
    concepts: list[DNAConceptInput]
    technologies: list[DNATechnologyInput]
    algorithms: list[str]
    definitions: list[str]
    equations: list[str]
    code_snippet_count: int
    references: list[str]
    cleaned_text: str
    related_document_candidates: list[RelatedDocumentCandidate] = field(default_factory=list)


@dataclass(frozen=True)
class DNAGraphNode:
    stable_key: str
    node_type: str
    name: str
    label: str
    description: str | None
    importance_score: float
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class DNAGraphEdge:
    source_key: str
    target_key: str
    edge_type: str
    weight: float
    confidence_score: float
    description: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeHierarchyItem:
    parent_topic: str
    child_topic: str
    hierarchy_type: str
    confidence_score: float
    evidence: str


@dataclass(frozen=True)
class LearningPathStep:
    order_index: int
    topic: str
    reason: str
    estimated_hours: int
    difficulty_level: str
    resource_hint: str


@dataclass(frozen=True)
class KnowledgeDNAResult:
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
    related_documents: list[RelatedDocumentCandidate]
    nodes: list[DNAGraphNode]
    edges: list[DNAGraphEdge]
    hierarchy: list[KnowledgeHierarchyItem]
    learning_path: list[LearningPathStep]
    metadata: dict[str, object]
