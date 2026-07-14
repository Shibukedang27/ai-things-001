"""create knowledge engine schema

Revision ID: 20260714_0002
Revises: 20260714_0001
Create Date: 2026-07-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0002"
down_revision: str | None = "20260714_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("author", sa.String(length=160), nullable=True),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("source_type", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("mime_type", sa.String(length=160), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("difficulty", sa.String(length=40), nullable=False),
        sa.Column("estimated_reading_time_minutes", sa.Integer(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("character_count", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("cleaned_text", sa.Text(), nullable=False),
        sa.Column("topics", sa.JSON(), nullable=False),
        sa.Column("definitions", sa.JSON(), nullable=False),
        sa.Column("algorithms", sa.JSON(), nullable=False),
        sa.Column("equations", sa.JSON(), nullable=False),
        sa.Column("code_snippets", sa.JSON(), nullable=False),
        sa.Column("learning_objectives", sa.JSON(), nullable=False),
        sa.Column("learning_assets", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_documents_created_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
        sa.UniqueConstraint("content_hash", name=op.f("uq_documents_content_hash")),
    )
    op.create_index(op.f("ix_documents_category"), "documents", ["category"])
    op.create_index(op.f("ix_documents_content_hash"), "documents", ["content_hash"])
    op.create_index(op.f("ix_documents_difficulty"), "documents", ["difficulty"])
    op.create_index(op.f("ix_documents_source_type"), "documents", ["source_type"])
    op.create_index(op.f("ix_documents_status"), "documents", ["status"])
    op.create_index(op.f("ix_documents_title"), "documents", ["title"])

    op.create_table(
        "document_chunks",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("character_count", sa.Integer(), nullable=False),
        sa.Column("start_char", sa.Integer(), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_chunks_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_chunks")),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_document_chunks_document_id_chunk_index"),
    )
    op.create_index(op.f("ix_document_chunks_content_hash"), "document_chunks", ["content_hash"])
    op.create_index(op.f("ix_document_chunks_document_id"), "document_chunks", ["document_id"])

    op.create_table(
        "document_concepts",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("normalized_name", sa.String(length=180), nullable=False),
        sa.Column("concept_type", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("prerequisites", sa.JSON(), nullable=False),
        sa.Column("dependencies", sa.JSON(), nullable=False),
        sa.Column("difficulty_level", sa.String(length=40), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_concepts_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_concepts")),
        sa.UniqueConstraint("document_id", "normalized_name", name="uq_document_concepts_document_id_name"),
    )
    op.create_index(op.f("ix_document_concepts_concept_type"), "document_concepts", ["concept_type"])
    op.create_index(op.f("ix_document_concepts_difficulty_level"), "document_concepts", ["difficulty_level"])
    op.create_index(op.f("ix_document_concepts_document_id"), "document_concepts", ["document_id"])
    op.create_index(op.f("ix_document_concepts_name"), "document_concepts", ["name"])
    op.create_index(op.f("ix_document_concepts_normalized_name"), "document_concepts", ["normalized_name"])

    op.create_table(
        "document_keywords",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("value", sa.String(length=140), nullable=False),
        sa.Column("normalized_value", sa.String(length=140), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False),
        sa.Column("occurrence_count", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_keywords_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_keywords")),
        sa.UniqueConstraint("document_id", "normalized_value", name="uq_document_keywords_document_id_value"),
    )
    op.create_index(op.f("ix_document_keywords_document_id"), "document_keywords", ["document_id"])
    op.create_index(op.f("ix_document_keywords_normalized_value"), "document_keywords", ["normalized_value"])
    op.create_index(op.f("ix_document_keywords_value"), "document_keywords", ["value"])

    op.create_table(
        "document_references",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=True),
        sa.Column("authors", sa.JSON(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=180), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("citation_text", sa.Text(), nullable=False),
        sa.Column("reference_type", sa.String(length=80), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_references_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_references")),
    )
    op.create_index(op.f("ix_document_references_document_id"), "document_references", ["document_id"])
    op.create_index(op.f("ix_document_references_reference_type"), "document_references", ["reference_type"])
    op.create_index(op.f("ix_document_references_year"), "document_references", ["year"])

    op.create_table(
        "document_summaries",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("summary_type", sa.String(length=60), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_summaries_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_summaries")),
        sa.UniqueConstraint("document_id", "summary_type", name="uq_document_summaries_document_id_type"),
    )
    op.create_index(op.f("ix_document_summaries_document_id"), "document_summaries", ["document_id"])
    op.create_index(op.f("ix_document_summaries_summary_type"), "document_summaries", ["summary_type"])

    op.create_table(
        "document_technologies",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("normalized_name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_technologies_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_technologies")),
        sa.UniqueConstraint("document_id", "normalized_name", name="uq_document_technologies_document_id_name"),
    )
    op.create_index(op.f("ix_document_technologies_category"), "document_technologies", ["category"])
    op.create_index(op.f("ix_document_technologies_document_id"), "document_technologies", ["document_id"])
    op.create_index(op.f("ix_document_technologies_name"), "document_technologies", ["name"])
    op.create_index(op.f("ix_document_technologies_normalized_name"), "document_technologies", ["normalized_name"])

    op.create_table(
        "document_embeddings",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_id", sa.String(length=36), nullable=True),
        sa.Column("embedding_model", sa.String(length=120), nullable=False),
        sa.Column("embedding_dimensions", sa.Integer(), nullable=False),
        sa.Column("vector", sa.JSON(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["document_chunks.id"],
            name=op.f("fk_document_embeddings_chunk_id_document_chunks"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_embeddings_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_embeddings")),
    )
    op.create_index(op.f("ix_document_embeddings_chunk_id"), "document_embeddings", ["chunk_id"])
    op.create_index(op.f("ix_document_embeddings_content_hash"), "document_embeddings", ["content_hash"])
    op.create_index(op.f("ix_document_embeddings_document_id"), "document_embeddings", ["document_id"])
    op.create_index(op.f("ix_document_embeddings_embedding_model"), "document_embeddings", ["embedding_model"])

    op.create_table(
        "knowledge_relationships",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("source_entity_type", sa.String(length=80), nullable=False),
        sa.Column("source_entity_id", sa.String(length=36), nullable=True),
        sa.Column("source_name", sa.String(length=180), nullable=False),
        sa.Column("target_entity_type", sa.String(length=80), nullable=False),
        sa.Column("target_entity_id", sa.String(length=36), nullable=True),
        sa.Column("target_name", sa.String(length=180), nullable=False),
        sa.Column("relationship_type", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_knowledge_relationships_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_relationships")),
    )
    op.create_index(op.f("ix_knowledge_relationships_document_id"), "knowledge_relationships", ["document_id"])
    op.create_index(
        op.f("ix_knowledge_relationships_relationship_type"),
        "knowledge_relationships",
        ["relationship_type"],
    )
    op.create_index(
        op.f("ix_knowledge_relationships_source_entity_id"),
        "knowledge_relationships",
        ["source_entity_id"],
    )
    op.create_index(
        op.f("ix_knowledge_relationships_source_entity_type"),
        "knowledge_relationships",
        ["source_entity_type"],
    )
    op.create_index(op.f("ix_knowledge_relationships_source_name"), "knowledge_relationships", ["source_name"])
    op.create_index(
        op.f("ix_knowledge_relationships_target_entity_id"),
        "knowledge_relationships",
        ["target_entity_id"],
    )
    op.create_index(
        op.f("ix_knowledge_relationships_target_entity_type"),
        "knowledge_relationships",
        ["target_entity_type"],
    )
    op.create_index(op.f("ix_knowledge_relationships_target_name"), "knowledge_relationships", ["target_name"])


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_relationships_target_name"), table_name="knowledge_relationships")
    op.drop_index(op.f("ix_knowledge_relationships_target_entity_type"), table_name="knowledge_relationships")
    op.drop_index(op.f("ix_knowledge_relationships_target_entity_id"), table_name="knowledge_relationships")
    op.drop_index(op.f("ix_knowledge_relationships_source_name"), table_name="knowledge_relationships")
    op.drop_index(op.f("ix_knowledge_relationships_source_entity_type"), table_name="knowledge_relationships")
    op.drop_index(op.f("ix_knowledge_relationships_source_entity_id"), table_name="knowledge_relationships")
    op.drop_index(op.f("ix_knowledge_relationships_relationship_type"), table_name="knowledge_relationships")
    op.drop_index(op.f("ix_knowledge_relationships_document_id"), table_name="knowledge_relationships")
    op.drop_table("knowledge_relationships")

    op.drop_index(op.f("ix_document_embeddings_embedding_model"), table_name="document_embeddings")
    op.drop_index(op.f("ix_document_embeddings_document_id"), table_name="document_embeddings")
    op.drop_index(op.f("ix_document_embeddings_content_hash"), table_name="document_embeddings")
    op.drop_index(op.f("ix_document_embeddings_chunk_id"), table_name="document_embeddings")
    op.drop_table("document_embeddings")

    op.drop_index(op.f("ix_document_technologies_normalized_name"), table_name="document_technologies")
    op.drop_index(op.f("ix_document_technologies_name"), table_name="document_technologies")
    op.drop_index(op.f("ix_document_technologies_document_id"), table_name="document_technologies")
    op.drop_index(op.f("ix_document_technologies_category"), table_name="document_technologies")
    op.drop_table("document_technologies")

    op.drop_index(op.f("ix_document_summaries_summary_type"), table_name="document_summaries")
    op.drop_index(op.f("ix_document_summaries_document_id"), table_name="document_summaries")
    op.drop_table("document_summaries")

    op.drop_index(op.f("ix_document_references_year"), table_name="document_references")
    op.drop_index(op.f("ix_document_references_reference_type"), table_name="document_references")
    op.drop_index(op.f("ix_document_references_document_id"), table_name="document_references")
    op.drop_table("document_references")

    op.drop_index(op.f("ix_document_keywords_value"), table_name="document_keywords")
    op.drop_index(op.f("ix_document_keywords_normalized_value"), table_name="document_keywords")
    op.drop_index(op.f("ix_document_keywords_document_id"), table_name="document_keywords")
    op.drop_table("document_keywords")

    op.drop_index(op.f("ix_document_concepts_normalized_name"), table_name="document_concepts")
    op.drop_index(op.f("ix_document_concepts_name"), table_name="document_concepts")
    op.drop_index(op.f("ix_document_concepts_document_id"), table_name="document_concepts")
    op.drop_index(op.f("ix_document_concepts_difficulty_level"), table_name="document_concepts")
    op.drop_index(op.f("ix_document_concepts_concept_type"), table_name="document_concepts")
    op.drop_table("document_concepts")

    op.drop_index(op.f("ix_document_chunks_document_id"), table_name="document_chunks")
    op.drop_index(op.f("ix_document_chunks_content_hash"), table_name="document_chunks")
    op.drop_table("document_chunks")

    op.drop_index(op.f("ix_documents_title"), table_name="documents")
    op.drop_index(op.f("ix_documents_status"), table_name="documents")
    op.drop_index(op.f("ix_documents_source_type"), table_name="documents")
    op.drop_index(op.f("ix_documents_difficulty"), table_name="documents")
    op.drop_index(op.f("ix_documents_content_hash"), table_name="documents")
    op.drop_index(op.f("ix_documents_category"), table_name="documents")
    op.drop_table("documents")
