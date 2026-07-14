"""create hybrid retrieval and reasoning schema

Revision ID: 20260714_0005
Revises: 20260714_0004
Create Date: 2026-07-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0005"
down_revision: str | None = "20260714_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "retrieval_embeddings",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_id", sa.String(length=36), nullable=True),
        sa.Column("namespace", sa.String(length=120), nullable=False),
        sa.Column("collection_name", sa.String(length=120), nullable=False),
        sa.Column("vector_store_backend", sa.String(length=80), nullable=False),
        sa.Column("embedding_model", sa.String(length=120), nullable=False),
        sa.Column("embedding_dimensions", sa.Integer(), nullable=False),
        sa.Column("vector", sa.JSON(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("cache_key", sa.String(length=128), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["document_chunks.id"],
            name=op.f("fk_retrieval_embeddings_chunk_id_document_chunks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_retrieval_embeddings_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_retrieval_embeddings")),
        sa.UniqueConstraint("cache_key", name=op.f("uq_retrieval_embeddings_cache_key")),
    )
    op.create_index(op.f("ix_retrieval_embeddings_cache_key"), "retrieval_embeddings", ["cache_key"])
    op.create_index(op.f("ix_retrieval_embeddings_chunk_id"), "retrieval_embeddings", ["chunk_id"])
    op.create_index(op.f("ix_retrieval_embeddings_collection_name"), "retrieval_embeddings", ["collection_name"])
    op.create_index(op.f("ix_retrieval_embeddings_content_hash"), "retrieval_embeddings", ["content_hash"])
    op.create_index(op.f("ix_retrieval_embeddings_document_id"), "retrieval_embeddings", ["document_id"])
    op.create_index(op.f("ix_retrieval_embeddings_embedding_model"), "retrieval_embeddings", ["embedding_model"])
    op.create_index(op.f("ix_retrieval_embeddings_namespace"), "retrieval_embeddings", ["namespace"])
    op.create_index(
        op.f("ix_retrieval_embeddings_vector_store_backend"),
        "retrieval_embeddings",
        ["vector_store_backend"],
    )

    op.create_table(
        "retrieval_queries",
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("normalized_query", sa.String(length=500), nullable=False),
        sa.Column("query_hash", sa.String(length=64), nullable=False),
        sa.Column("intent", sa.String(length=80), nullable=False),
        sa.Column("expanded_queries", sa.JSON(), nullable=False),
        sa.Column("filters", sa.JSON(), nullable=False),
        sa.Column("requested_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            name=op.f("fk_retrieval_queries_requested_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_retrieval_queries")),
    )
    op.create_index(op.f("ix_retrieval_queries_intent"), "retrieval_queries", ["intent"])
    op.create_index(op.f("ix_retrieval_queries_normalized_query"), "retrieval_queries", ["normalized_query"])
    op.create_index(op.f("ix_retrieval_queries_query_hash"), "retrieval_queries", ["query_hash"])
    op.create_index(op.f("ix_retrieval_queries_requested_by_user_id"), "retrieval_queries", ["requested_by_user_id"])

    op.create_table(
        "knowledge_cache",
        sa.Column("cache_key", sa.String(length=128), nullable=False),
        sa.Column("cache_type", sa.String(length=80), nullable=False),
        sa.Column("query_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hit_count", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_cache")),
        sa.UniqueConstraint("cache_key", name=op.f("uq_knowledge_cache_cache_key")),
    )
    op.create_index(op.f("ix_knowledge_cache_cache_key"), "knowledge_cache", ["cache_key"])
    op.create_index(op.f("ix_knowledge_cache_cache_type"), "knowledge_cache", ["cache_type"])
    op.create_index(op.f("ix_knowledge_cache_query_hash"), "knowledge_cache", ["query_hash"])

    op.create_table(
        "retrieval_history",
        sa.Column("query_id", sa.String(length=36), nullable=False),
        sa.Column("mode", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), nullable=False),
        sa.Column("source_documents", sa.JSON(), nullable=False),
        sa.Column("retrieved_sections", sa.JSON(), nullable=False),
        sa.Column("reasoning_path", sa.JSON(), nullable=False),
        sa.Column("supporting_evidence", sa.JSON(), nullable=False),
        sa.Column("validation", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["query_id"],
            ["retrieval_queries.id"],
            name=op.f("fk_retrieval_history_query_id_retrieval_queries"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_retrieval_history")),
    )
    op.create_index(op.f("ix_retrieval_history_mode"), "retrieval_history", ["mode"])
    op.create_index(op.f("ix_retrieval_history_query_id"), "retrieval_history", ["query_id"])
    op.create_index(op.f("ix_retrieval_history_status"), "retrieval_history", ["status"])

    op.create_table(
        "reasoning_logs",
        sa.Column("retrieval_history_id", sa.String(length=36), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("step_type", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["retrieval_history_id"],
            ["retrieval_history.id"],
            name=op.f("fk_reasoning_logs_retrieval_history_id_retrieval_history"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reasoning_logs")),
    )
    op.create_index(op.f("ix_reasoning_logs_retrieval_history_id"), "reasoning_logs", ["retrieval_history_id"])
    op.create_index(op.f("ix_reasoning_logs_step_type"), "reasoning_logs", ["step_type"])

    op.create_table(
        "citation_history",
        sa.Column("retrieval_history_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("chunk_id", sa.String(length=36), nullable=True),
        sa.Column("citation_key", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("snippet", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("section_label", sa.String(length=120), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["document_chunks.id"],
            name=op.f("fk_citation_history_chunk_id_document_chunks"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_citation_history_document_id_documents"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["retrieval_history_id"],
            ["retrieval_history.id"],
            name=op.f("fk_citation_history_retrieval_history_id_retrieval_history"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_citation_history")),
    )
    op.create_index(op.f("ix_citation_history_chunk_id"), "citation_history", ["chunk_id"])
    op.create_index(op.f("ix_citation_history_citation_key"), "citation_history", ["citation_key"])
    op.create_index(op.f("ix_citation_history_document_id"), "citation_history", ["document_id"])
    op.create_index(op.f("ix_citation_history_retrieval_history_id"), "citation_history", ["retrieval_history_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_citation_history_retrieval_history_id"), table_name="citation_history")
    op.drop_index(op.f("ix_citation_history_document_id"), table_name="citation_history")
    op.drop_index(op.f("ix_citation_history_citation_key"), table_name="citation_history")
    op.drop_index(op.f("ix_citation_history_chunk_id"), table_name="citation_history")
    op.drop_table("citation_history")

    op.drop_index(op.f("ix_reasoning_logs_step_type"), table_name="reasoning_logs")
    op.drop_index(op.f("ix_reasoning_logs_retrieval_history_id"), table_name="reasoning_logs")
    op.drop_table("reasoning_logs")

    op.drop_index(op.f("ix_retrieval_history_status"), table_name="retrieval_history")
    op.drop_index(op.f("ix_retrieval_history_query_id"), table_name="retrieval_history")
    op.drop_index(op.f("ix_retrieval_history_mode"), table_name="retrieval_history")
    op.drop_table("retrieval_history")

    op.drop_index(op.f("ix_knowledge_cache_query_hash"), table_name="knowledge_cache")
    op.drop_index(op.f("ix_knowledge_cache_cache_type"), table_name="knowledge_cache")
    op.drop_index(op.f("ix_knowledge_cache_cache_key"), table_name="knowledge_cache")
    op.drop_table("knowledge_cache")

    op.drop_index(op.f("ix_retrieval_queries_requested_by_user_id"), table_name="retrieval_queries")
    op.drop_index(op.f("ix_retrieval_queries_query_hash"), table_name="retrieval_queries")
    op.drop_index(op.f("ix_retrieval_queries_normalized_query"), table_name="retrieval_queries")
    op.drop_index(op.f("ix_retrieval_queries_intent"), table_name="retrieval_queries")
    op.drop_table("retrieval_queries")

    op.drop_index(op.f("ix_retrieval_embeddings_vector_store_backend"), table_name="retrieval_embeddings")
    op.drop_index(op.f("ix_retrieval_embeddings_namespace"), table_name="retrieval_embeddings")
    op.drop_index(op.f("ix_retrieval_embeddings_embedding_model"), table_name="retrieval_embeddings")
    op.drop_index(op.f("ix_retrieval_embeddings_document_id"), table_name="retrieval_embeddings")
    op.drop_index(op.f("ix_retrieval_embeddings_content_hash"), table_name="retrieval_embeddings")
    op.drop_index(op.f("ix_retrieval_embeddings_collection_name"), table_name="retrieval_embeddings")
    op.drop_index(op.f("ix_retrieval_embeddings_chunk_id"), table_name="retrieval_embeddings")
    op.drop_index(op.f("ix_retrieval_embeddings_cache_key"), table_name="retrieval_embeddings")
    op.drop_table("retrieval_embeddings")
