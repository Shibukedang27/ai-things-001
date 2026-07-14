from typing import Any

from pydantic import Field

from backend.schemas.common import APIModel, TimestampedRead


class MultiAgentAnalysisRequest(APIModel):
    document_id: str
    include_agents: list[str] | None = None
    timeout_seconds: float | None = Field(default=None, gt=0, le=60)
    request_options: dict[str, Any] = Field(default_factory=dict)


class AgentStatusRead(TimestampedRead):
    id: str
    role: str
    name: str
    description: str
    status: str
    default_priority: int
    timeout_seconds: float
    max_retries: int
    capabilities: list[str]


class AgentResponseRead(TimestampedRead):
    id: str
    agent_role: str
    title: str
    summary: str
    confidence_score: float
    response_data: dict[str, Any]
    warnings: list[str]
    sources: list[str]


class AgentTaskRead(TimestampedRead):
    id: str
    pipeline_id: str
    agent_id: str | None
    agent_role: str
    status: str
    priority: int
    attempts: int
    max_retries: int
    timeout_seconds: float
    duration_ms: int
    error_message: str | None
    task_payload: dict[str, Any]
    responses: list[AgentResponseRead] = Field(default_factory=list)


class ExecutionLogRead(TimestampedRead):
    id: str
    pipeline_id: str
    task_id: str | None
    event_type: str
    agent_role: str | None
    message: str
    metadata_json: dict[str, Any]


class PipelineHistoryRead(TimestampedRead):
    id: str
    document_id: str
    knowledge_dna_id: str | None
    requested_by_user_id: str | None
    status: str
    final_response: dict[str, Any]
    request_options: dict[str, Any]
    error_message: str | None
    tasks: list[AgentTaskRead] = Field(default_factory=list)
    logs: list[ExecutionLogRead] = Field(default_factory=list)


class PipelineStatusRead(APIModel):
    pipeline_id: str
    status: str
    document_id: str
    task_count: int
    completed_tasks: int
    failed_tasks: int
    canceled_tasks: int


class TaskActionResponse(APIModel):
    task_id: str
    status: str
    message: str
