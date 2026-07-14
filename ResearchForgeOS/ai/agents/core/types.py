from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AgentRole(StrEnum):
    RESEARCH = "research_agent"
    CONCEPT = "concept_agent"
    TEACHER = "teacher_agent"
    CODE = "code_agent"
    QUIZ = "quiz_agent"
    SUMMARY = "summary_agent"
    CITATION = "citation_agent"
    ROADMAP = "roadmap_agent"
    KNOWLEDGE_GRAPH = "knowledge_graph_agent"
    QUALITY_ASSURANCE = "quality_assurance_agent"


class AgentStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    RETRYING = "retrying"


class PipelineStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass(frozen=True)
class AgentDocument:
    id: str
    title: str
    category: str
    difficulty: str
    estimated_reading_time_minutes: int
    topics: list[str]
    cleaned_text: str
    summaries: dict[str, str]
    concepts: list[dict[str, Any]]
    keywords: list[str]
    technologies: list[dict[str, Any]]
    algorithms: list[str]
    definitions: list[dict[str, str]]
    code_snippets: list[dict[str, str]]
    references: list[dict[str, Any]]


@dataclass(frozen=True)
class AgentDNA:
    id: str | None
    research_category: str | None
    knowledge_score: float | None
    interview_importance: float | None
    industry_relevance: float | None
    implementation_complexity: float | None
    primary_concepts: list[str]
    secondary_concepts: list[str]
    prerequisites: list[str]
    future_learning_topics: list[str]
    learning_order: list[str]
    estimated_mastery_time_hours: int | None
    parent_topics: list[str]
    child_topics: list[str]
    sibling_topics: list[str]
    knowledge_chains: list[list[str]]
    research_evolution: list[str]


@dataclass(frozen=True)
class AgentExecutionContext:
    document: AgentDocument
    dna: AgentDNA | None
    previous_outputs: dict[AgentRole, AgentOutput] = field(default_factory=dict)
    request_options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentTaskPayload:
    pipeline_id: str
    task_id: str
    role: AgentRole
    priority: int
    timeout_seconds: float
    max_retries: int
    context: AgentExecutionContext


@dataclass(frozen=True)
class AgentOutput:
    role: AgentRole
    title: str
    summary: str
    confidence_score: float
    data: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AgentTaskResult:
    task_id: str
    role: AgentRole
    status: TaskStatus
    output: AgentOutput | None
    attempts: int
    duration_ms: int
    error_message: str | None = None


@dataclass(frozen=True)
class AgentRunResult:
    pipeline_id: str
    status: PipelineStatus
    outputs: list[AgentOutput]
    final_response: dict[str, Any]
    task_results: list[AgentTaskResult]
    execution_log: list[dict[str, Any]]
