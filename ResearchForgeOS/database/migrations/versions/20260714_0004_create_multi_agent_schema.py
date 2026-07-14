"""create multi agent research schema

Revision ID: 20260714_0004
Revises: 20260714_0003
Create Date: 2026-07-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0004"
down_revision: str | None = "20260714_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("role", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("default_priority", sa.Integer(), nullable=False),
        sa.Column("timeout_seconds", sa.Float(), nullable=False),
        sa.Column("max_retries", sa.Integer(), nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agents")),
        sa.UniqueConstraint("role", name=op.f("uq_agents_role")),
    )
    op.create_index(op.f("ix_agents_role"), "agents", ["role"])
    op.create_index(op.f("ix_agents_status"), "agents", ["status"])

    op.create_table(
        "pipeline_history",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("knowledge_dna_id", sa.String(length=36), nullable=True),
        sa.Column("requested_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("final_response", sa.JSON(), nullable=False),
        sa.Column("request_options", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_pipeline_history_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["knowledge_dna_id"],
            ["knowledge_dna.id"],
            name=op.f("fk_pipeline_history_knowledge_dna_id_knowledge_dna"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            name=op.f("fk_pipeline_history_requested_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pipeline_history")),
    )
    op.create_index(op.f("ix_pipeline_history_document_id"), "pipeline_history", ["document_id"])
    op.create_index(op.f("ix_pipeline_history_knowledge_dna_id"), "pipeline_history", ["knowledge_dna_id"])
    op.create_index(op.f("ix_pipeline_history_requested_by_user_id"), "pipeline_history", ["requested_by_user_id"])
    op.create_index(op.f("ix_pipeline_history_status"), "pipeline_history", ["status"])

    op.create_table(
        "agent_tasks",
        sa.Column("pipeline_id", sa.String(length=36), nullable=False),
        sa.Column("agent_id", sa.String(length=36), nullable=True),
        sa.Column("agent_role", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("max_retries", sa.Integer(), nullable=False),
        sa.Column("timeout_seconds", sa.Float(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("task_payload", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name=op.f("fk_agent_tasks_agent_id_agents"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["pipeline_id"],
            ["pipeline_history.id"],
            name=op.f("fk_agent_tasks_pipeline_id_pipeline_history"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_tasks")),
    )
    op.create_index(op.f("ix_agent_tasks_agent_id"), "agent_tasks", ["agent_id"])
    op.create_index(op.f("ix_agent_tasks_agent_role"), "agent_tasks", ["agent_role"])
    op.create_index(op.f("ix_agent_tasks_pipeline_id"), "agent_tasks", ["pipeline_id"])
    op.create_index(op.f("ix_agent_tasks_status"), "agent_tasks", ["status"])

    op.create_table(
        "agent_responses",
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("agent_role", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("response_data", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["agent_tasks.id"],
            name=op.f("fk_agent_responses_task_id_agent_tasks"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_responses")),
    )
    op.create_index(op.f("ix_agent_responses_agent_role"), "agent_responses", ["agent_role"])
    op.create_index(op.f("ix_agent_responses_task_id"), "agent_responses", ["task_id"])

    op.create_table(
        "execution_logs",
        sa.Column("pipeline_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("agent_role", sa.String(length=80), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["pipeline_id"],
            ["pipeline_history.id"],
            name=op.f("fk_execution_logs_pipeline_id_pipeline_history"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["agent_tasks.id"],
            name=op.f("fk_execution_logs_task_id_agent_tasks"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_execution_logs")),
    )
    op.create_index(op.f("ix_execution_logs_agent_role"), "execution_logs", ["agent_role"])
    op.create_index(op.f("ix_execution_logs_event_type"), "execution_logs", ["event_type"])
    op.create_index(op.f("ix_execution_logs_pipeline_id"), "execution_logs", ["pipeline_id"])
    op.create_index(op.f("ix_execution_logs_task_id"), "execution_logs", ["task_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_execution_logs_task_id"), table_name="execution_logs")
    op.drop_index(op.f("ix_execution_logs_pipeline_id"), table_name="execution_logs")
    op.drop_index(op.f("ix_execution_logs_event_type"), table_name="execution_logs")
    op.drop_index(op.f("ix_execution_logs_agent_role"), table_name="execution_logs")
    op.drop_table("execution_logs")

    op.drop_index(op.f("ix_agent_responses_task_id"), table_name="agent_responses")
    op.drop_index(op.f("ix_agent_responses_agent_role"), table_name="agent_responses")
    op.drop_table("agent_responses")

    op.drop_index(op.f("ix_agent_tasks_status"), table_name="agent_tasks")
    op.drop_index(op.f("ix_agent_tasks_pipeline_id"), table_name="agent_tasks")
    op.drop_index(op.f("ix_agent_tasks_agent_role"), table_name="agent_tasks")
    op.drop_index(op.f("ix_agent_tasks_agent_id"), table_name="agent_tasks")
    op.drop_table("agent_tasks")

    op.drop_index(op.f("ix_pipeline_history_status"), table_name="pipeline_history")
    op.drop_index(op.f("ix_pipeline_history_requested_by_user_id"), table_name="pipeline_history")
    op.drop_index(op.f("ix_pipeline_history_knowledge_dna_id"), table_name="pipeline_history")
    op.drop_index(op.f("ix_pipeline_history_document_id"), table_name="pipeline_history")
    op.drop_table("pipeline_history")

    op.drop_index(op.f("ix_agents_status"), table_name="agents")
    op.drop_index(op.f("ix_agents_role"), table_name="agents")
    op.drop_table("agents")
