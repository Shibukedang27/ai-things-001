from __future__ import annotations

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Agent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agents"

    role: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    default_priority: Mapped[int] = mapped_column(Integer, nullable=False)
    timeout_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False)
    capabilities: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)


class PipelineHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "pipeline_history"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    knowledge_dna_id: Mapped[str | None] = mapped_column(
        ForeignKey("knowledge_dna.id", ondelete="SET NULL"),
        index=True,
    )
    requested_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    final_response: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    request_options: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    tasks: Mapped[list[AgentTask]] = relationship(
        "AgentTask",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    logs: Mapped[list[ExecutionLog]] = relationship(
        "ExecutionLog",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AgentTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_tasks"

    pipeline_id: Mapped[str] = mapped_column(ForeignKey("pipeline_history.id", ondelete="CASCADE"), index=True)
    agent_id: Mapped[str | None] = mapped_column(ForeignKey("agents.id", ondelete="SET NULL"), index=True)
    agent_role: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False)
    timeout_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    pipeline: Mapped[PipelineHistory] = relationship("PipelineHistory", back_populates="tasks")
    agent: Mapped[Agent | None] = relationship("Agent")
    responses: Mapped[list[AgentResponse]] = relationship(
        "AgentResponse",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AgentResponse(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_responses"

    task_id: Mapped[str] = mapped_column(ForeignKey("agent_tasks.id", ondelete="CASCADE"), index=True)
    agent_role: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    response_data: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    warnings: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    sources: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    task: Mapped[AgentTask] = relationship("AgentTask", back_populates="responses")


class ExecutionLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "execution_logs"

    pipeline_id: Mapped[str] = mapped_column(ForeignKey("pipeline_history.id", ondelete="CASCADE"), index=True)
    task_id: Mapped[str | None] = mapped_column(ForeignKey("agent_tasks.id", ondelete="SET NULL"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    agent_role: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    pipeline: Mapped[PipelineHistory] = relationship("PipelineHistory", back_populates="logs")
    task: Mapped[AgentTask | None] = relationship("AgentTask")
