from dataclasses import dataclass, field
from enum import StrEnum


class SourceType(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "markdown"
    POWERPOINT = "powerpoint"
    RESEARCH_PAPER = "research_paper"
    GITHUB_REPOSITORY = "github_repository"
    WEBSITE = "website"
    YOUTUBE_TRANSCRIPT = "youtube_transcript"
    PLAIN_NOTES = "plain_notes"


class DifficultyLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass(frozen=True)
class KnowledgeSourceRequest:
    source_type: SourceType | None = None
    filename: str | None = None
    mime_type: str | None = None
    content: bytes | str | None = None
    source_url: str | None = None
    title: str | None = None
    author: str | None = None
    category: str | None = None


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    source_type: SourceType
    title: str | None = None
    author: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class TextChunk:
    index: int
    content: str
    start_char: int
    end_char: int
    token_count: int
    content_hash: str


@dataclass(frozen=True)
class SummaryBundle:
    executive_summary: str
    beginner_summary: str
    technical_summary: str
    detailed_summary: str
    one_minute_summary: str
    five_minute_summary: str


@dataclass(frozen=True)
class ConceptCandidate:
    name: str
    description: str
    concept_type: str
    prerequisites: list[str]
    dependencies: list[str]
    difficulty_level: DifficultyLevel
    confidence_score: float


@dataclass(frozen=True)
class KeywordCandidate:
    value: str
    occurrence_count: int
    relevance_score: float


@dataclass(frozen=True)
class TechnologyCandidate:
    name: str
    category: str
    confidence_score: float
    evidence: list[str]


@dataclass(frozen=True)
class ReferenceCandidate:
    title: str | None
    authors: list[str]
    year: int | None
    source: str | None
    url: str | None
    citation_text: str
    reference_type: str
    confidence_score: float


@dataclass(frozen=True)
class EmbeddingRecord:
    chunk_index: int
    embedding_model: str
    embedding_dimensions: int
    vector: list[float]
    content_hash: str
    metadata: dict[str, object]


@dataclass(frozen=True)
class RelationshipCandidate:
    source_name: str
    target_name: str
    relationship_type: str
    description: str
    confidence_score: float
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class LearningAssets:
    learning_objectives: list[str]
    flashcards: list[dict[str, str]]
    quiz_questions: list[dict[str, object]]
    interview_questions: list[str]
    daily_revision_plan: list[str]


@dataclass(frozen=True)
class KnowledgeMetadata:
    title: str
    author: str | None
    category: str
    topics: list[str]
    difficulty: DifficultyLevel
    estimated_reading_time_minutes: int
    word_count: int
    character_count: int
    language: str
    content_hash: str


@dataclass(frozen=True)
class KnowledgeEngineResult:
    source_type: SourceType
    cleaned_text: str
    metadata: KnowledgeMetadata
    chunks: list[TextChunk]
    summaries: SummaryBundle
    concepts: list[ConceptCandidate]
    keywords: list[KeywordCandidate]
    technologies: list[TechnologyCandidate]
    definitions: list[dict[str, str]]
    algorithms: list[dict[str, str]]
    equations: list[dict[str, str]]
    code_snippets: list[dict[str, str]]
    references: list[ReferenceCandidate]
    embeddings: list[EmbeddingRecord]
    relationships: list[RelationshipCandidate]
    learning_assets: LearningAssets
