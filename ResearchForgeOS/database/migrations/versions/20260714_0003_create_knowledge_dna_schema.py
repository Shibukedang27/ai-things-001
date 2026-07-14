"""create knowledge dna schema

Revision ID: 20260714_0003
Revises: 20260714_0002
Create Date: 2026-07-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0003"
down_revision: str | None = "20260714_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_dna",
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("document_title", sa.String(length=240), nullable=False),
        sa.Column("difficulty_level", sa.String(length=40), nullable=False),
        sa.Column("estimated_reading_time_minutes", sa.Integer(), nullable=False),
        sa.Column("knowledge_score", sa.Float(), nullable=False),
        sa.Column("interview_importance", sa.Float(), nullable=False),
        sa.Column("industry_relevance", sa.Float(), nullable=False),
        sa.Column("implementation_complexity", sa.Float(), nullable=False),
        sa.Column("research_category", sa.String(length=120), nullable=False),
        sa.Column("primary_concepts", sa.JSON(), nullable=False),
        sa.Column("secondary_concepts", sa.JSON(), nullable=False),
        sa.Column("prerequisites", sa.JSON(), nullable=False),
        sa.Column("advanced_topics", sa.JSON(), nullable=False),
        sa.Column("future_learning_topics", sa.JSON(), nullable=False),
        sa.Column("technologies_used", sa.JSON(), nullable=False),
        sa.Column("programming_languages", sa.JSON(), nullable=False),
        sa.Column("frameworks", sa.JSON(), nullable=False),
        sa.Column("libraries", sa.JSON(), nullable=False),
        sa.Column("algorithms", sa.JSON(), nullable=False),
        sa.Column("datasets", sa.JSON(), nullable=False),
        sa.Column("research_papers", sa.JSON(), nullable=False),
        sa.Column("learning_order", sa.JSON(), nullable=False),
        sa.Column("estimated_mastery_time_hours", sa.Integer(), nullable=False),
        sa.Column("mathematical_topics", sa.JSON(), nullable=False),
        sa.Column("parent_topics", sa.JSON(), nullable=False),
        sa.Column("child_topics", sa.JSON(), nullable=False),
        sa.Column("sibling_topics", sa.JSON(), nullable=False),
        sa.Column("knowledge_chains", sa.JSON(), nullable=False),
        sa.Column("research_evolution", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_knowledge_dna_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_dna")),
        sa.UniqueConstraint("document_id", name=op.f("uq_knowledge_dna_document_id")),
    )
    op.create_index(op.f("ix_knowledge_dna_difficulty_level"), "knowledge_dna", ["difficulty_level"])
    op.create_index(op.f("ix_knowledge_dna_document_id"), "knowledge_dna", ["document_id"])
    op.create_index(op.f("ix_knowledge_dna_document_title"), "knowledge_dna", ["document_title"])
    op.create_index(op.f("ix_knowledge_dna_research_category"), "knowledge_dna", ["research_category"])

    op.create_table(
        "knowledge_nodes",
        sa.Column("knowledge_dna_id", sa.String(length=36), nullable=False),
        sa.Column("stable_key", sa.String(length=240), nullable=False),
        sa.Column("node_type", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("label", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("importance_score", sa.Float(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_dna_id"],
            ["knowledge_dna.id"],
            name=op.f("fk_knowledge_nodes_knowledge_dna_id_knowledge_dna"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_nodes")),
        sa.UniqueConstraint("knowledge_dna_id", "stable_key", name="uq_knowledge_nodes_dna_key"),
    )
    op.create_index(op.f("ix_knowledge_nodes_knowledge_dna_id"), "knowledge_nodes", ["knowledge_dna_id"])
    op.create_index(op.f("ix_knowledge_nodes_name"), "knowledge_nodes", ["name"])
    op.create_index(op.f("ix_knowledge_nodes_node_type"), "knowledge_nodes", ["node_type"])
    op.create_index(op.f("ix_knowledge_nodes_stable_key"), "knowledge_nodes", ["stable_key"])

    op.create_table(
        "knowledge_hierarchy",
        sa.Column("knowledge_dna_id", sa.String(length=36), nullable=False),
        sa.Column("parent_topic", sa.String(length=180), nullable=False),
        sa.Column("child_topic", sa.String(length=180), nullable=False),
        sa.Column("hierarchy_type", sa.String(length=80), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_dna_id"],
            ["knowledge_dna.id"],
            name=op.f("fk_knowledge_hierarchy_knowledge_dna_id_knowledge_dna"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_hierarchy")),
    )
    op.create_index(op.f("ix_knowledge_hierarchy_child_topic"), "knowledge_hierarchy", ["child_topic"])
    op.create_index(op.f("ix_knowledge_hierarchy_hierarchy_type"), "knowledge_hierarchy", ["hierarchy_type"])
    op.create_index(op.f("ix_knowledge_hierarchy_knowledge_dna_id"), "knowledge_hierarchy", ["knowledge_dna_id"])
    op.create_index(op.f("ix_knowledge_hierarchy_parent_topic"), "knowledge_hierarchy", ["parent_topic"])

    op.create_table(
        "learning_path",
        sa.Column("knowledge_dna_id", sa.String(length=36), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=180), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("estimated_hours", sa.Integer(), nullable=False),
        sa.Column("difficulty_level", sa.String(length=40), nullable=False),
        sa.Column("resource_hint", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_dna_id"],
            ["knowledge_dna.id"],
            name=op.f("fk_learning_path_knowledge_dna_id_knowledge_dna"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_learning_path")),
        sa.UniqueConstraint("knowledge_dna_id", "order_index", name="uq_learning_path_dna_order"),
    )
    op.create_index(op.f("ix_learning_path_difficulty_level"), "learning_path", ["difficulty_level"])
    op.create_index(op.f("ix_learning_path_knowledge_dna_id"), "learning_path", ["knowledge_dna_id"])
    op.create_index(op.f("ix_learning_path_topic"), "learning_path", ["topic"])

    op.create_table(
        "prerequisites",
        sa.Column("knowledge_dna_id", sa.String(length=36), nullable=False),
        sa.Column("topic", sa.String(length=180), nullable=False),
        sa.Column("prerequisite_type", sa.String(length=80), nullable=False),
        sa.Column("importance_score", sa.Float(), nullable=False),
        sa.Column("source_concept", sa.String(length=180), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_dna_id"],
            ["knowledge_dna.id"],
            name=op.f("fk_prerequisites_knowledge_dna_id_knowledge_dna"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prerequisites")),
    )
    op.create_index(op.f("ix_prerequisites_knowledge_dna_id"), "prerequisites", ["knowledge_dna_id"])
    op.create_index(op.f("ix_prerequisites_prerequisite_type"), "prerequisites", ["prerequisite_type"])
    op.create_index(op.f("ix_prerequisites_topic"), "prerequisites", ["topic"])

    op.create_table(
        "related_documents",
        sa.Column("knowledge_dna_id", sa.String(length=36), nullable=False),
        sa.Column("related_document_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("shared_signals", sa.JSON(), nullable=False),
        sa.Column("relationship_reason", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_dna_id"],
            ["knowledge_dna.id"],
            name=op.f("fk_related_documents_knowledge_dna_id_knowledge_dna"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["related_document_id"],
            ["documents.id"],
            name=op.f("fk_related_documents_related_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_related_documents")),
        sa.UniqueConstraint("knowledge_dna_id", "related_document_id", name="uq_related_documents_dna_document"),
    )
    op.create_index(op.f("ix_related_documents_knowledge_dna_id"), "related_documents", ["knowledge_dna_id"])
    op.create_index(op.f("ix_related_documents_related_document_id"), "related_documents", ["related_document_id"])

    op.create_table(
        "knowledge_edges",
        sa.Column("knowledge_dna_id", sa.String(length=36), nullable=False),
        sa.Column("source_node_id", sa.String(length=36), nullable=True),
        sa.Column("target_node_id", sa.String(length=36), nullable=True),
        sa.Column("source_key", sa.String(length=240), nullable=False),
        sa.Column("target_key", sa.String(length=240), nullable=False),
        sa.Column("edge_type", sa.String(length=80), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["knowledge_dna_id"],
            ["knowledge_dna.id"],
            name=op.f("fk_knowledge_edges_knowledge_dna_id_knowledge_dna"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_node_id"],
            ["knowledge_nodes.id"],
            name=op.f("fk_knowledge_edges_source_node_id_knowledge_nodes"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["target_node_id"],
            ["knowledge_nodes.id"],
            name=op.f("fk_knowledge_edges_target_node_id_knowledge_nodes"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_edges")),
    )
    op.create_index(op.f("ix_knowledge_edges_edge_type"), "knowledge_edges", ["edge_type"])
    op.create_index(op.f("ix_knowledge_edges_knowledge_dna_id"), "knowledge_edges", ["knowledge_dna_id"])
    op.create_index(op.f("ix_knowledge_edges_source_key"), "knowledge_edges", ["source_key"])
    op.create_index(op.f("ix_knowledge_edges_source_node_id"), "knowledge_edges", ["source_node_id"])
    op.create_index(op.f("ix_knowledge_edges_target_key"), "knowledge_edges", ["target_key"])
    op.create_index(op.f("ix_knowledge_edges_target_node_id"), "knowledge_edges", ["target_node_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_edges_target_node_id"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_target_key"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_source_node_id"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_source_key"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_knowledge_dna_id"), table_name="knowledge_edges")
    op.drop_index(op.f("ix_knowledge_edges_edge_type"), table_name="knowledge_edges")
    op.drop_table("knowledge_edges")

    op.drop_index(op.f("ix_related_documents_related_document_id"), table_name="related_documents")
    op.drop_index(op.f("ix_related_documents_knowledge_dna_id"), table_name="related_documents")
    op.drop_table("related_documents")

    op.drop_index(op.f("ix_prerequisites_topic"), table_name="prerequisites")
    op.drop_index(op.f("ix_prerequisites_prerequisite_type"), table_name="prerequisites")
    op.drop_index(op.f("ix_prerequisites_knowledge_dna_id"), table_name="prerequisites")
    op.drop_table("prerequisites")

    op.drop_index(op.f("ix_learning_path_topic"), table_name="learning_path")
    op.drop_index(op.f("ix_learning_path_knowledge_dna_id"), table_name="learning_path")
    op.drop_index(op.f("ix_learning_path_difficulty_level"), table_name="learning_path")
    op.drop_table("learning_path")

    op.drop_index(op.f("ix_knowledge_hierarchy_parent_topic"), table_name="knowledge_hierarchy")
    op.drop_index(op.f("ix_knowledge_hierarchy_knowledge_dna_id"), table_name="knowledge_hierarchy")
    op.drop_index(op.f("ix_knowledge_hierarchy_hierarchy_type"), table_name="knowledge_hierarchy")
    op.drop_index(op.f("ix_knowledge_hierarchy_child_topic"), table_name="knowledge_hierarchy")
    op.drop_table("knowledge_hierarchy")

    op.drop_index(op.f("ix_knowledge_nodes_stable_key"), table_name="knowledge_nodes")
    op.drop_index(op.f("ix_knowledge_nodes_node_type"), table_name="knowledge_nodes")
    op.drop_index(op.f("ix_knowledge_nodes_name"), table_name="knowledge_nodes")
    op.drop_index(op.f("ix_knowledge_nodes_knowledge_dna_id"), table_name="knowledge_nodes")
    op.drop_table("knowledge_nodes")

    op.drop_index(op.f("ix_knowledge_dna_research_category"), table_name="knowledge_dna")
    op.drop_index(op.f("ix_knowledge_dna_document_title"), table_name="knowledge_dna")
    op.drop_index(op.f("ix_knowledge_dna_document_id"), table_name="knowledge_dna")
    op.drop_index(op.f("ix_knowledge_dna_difficulty_level"), table_name="knowledge_dna")
    op.drop_table("knowledge_dna")
