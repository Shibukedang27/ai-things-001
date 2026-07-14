"""create interactive knowledge graph schema

Revision ID: 20260714_0006
Revises: 20260714_0005
Create Date: 2026-07-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260714_0006"
down_revision: str | None = "20260714_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "graph_nodes",
        sa.Column("stable_key", sa.String(length=260), nullable=False),
        sa.Column("node_type", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("label", sa.String(length=240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=True),
        sa.Column("importance_score", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("degree", sa.Integer(), nullable=False),
        sa.Column("cluster_id", sa.String(length=80), nullable=True),
        sa.Column("is_collapsed", sa.Boolean(), nullable=False),
        sa.Column("position_x", sa.Float(), nullable=False),
        sa.Column("position_y", sa.Float(), nullable=False),
        sa.Column("size", sa.Float(), nullable=False),
        sa.Column("color", sa.String(length=24), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_graph_nodes_document_id_documents"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_graph_nodes")),
        sa.UniqueConstraint("stable_key", name="uq_graph_nodes_stable_key"),
    )
    op.create_index(op.f("ix_graph_nodes_cluster_id"), "graph_nodes", ["cluster_id"])
    op.create_index(op.f("ix_graph_nodes_document_id"), "graph_nodes", ["document_id"])
    op.create_index(op.f("ix_graph_nodes_importance_score"), "graph_nodes", ["importance_score"])
    op.create_index(op.f("ix_graph_nodes_is_collapsed"), "graph_nodes", ["is_collapsed"])
    op.create_index(op.f("ix_graph_nodes_label"), "graph_nodes", ["label"])
    op.create_index(op.f("ix_graph_nodes_name"), "graph_nodes", ["name"])
    op.create_index(op.f("ix_graph_nodes_node_type"), "graph_nodes", ["node_type"])
    op.create_index(op.f("ix_graph_nodes_stable_key"), "graph_nodes", ["stable_key"])

    op.create_table(
        "graph_layouts",
        sa.Column("layout_name", sa.String(length=120), nullable=False),
        sa.Column("algorithm", sa.String(length=80), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("viewport", sa.JSON(), nullable=False),
        sa.Column("positions", sa.JSON(), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_graph_layouts")),
    )
    op.create_index(op.f("ix_graph_layouts_algorithm"), "graph_layouts", ["algorithm"])
    op.create_index(op.f("ix_graph_layouts_is_default"), "graph_layouts", ["is_default"])
    op.create_index(op.f("ix_graph_layouts_layout_name"), "graph_layouts", ["layout_name"])

    op.create_table(
        "graph_snapshots",
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("snapshot_type", sa.String(length=80), nullable=False),
        sa.Column("node_count", sa.Integer(), nullable=False),
        sa.Column("edge_count", sa.Integer(), nullable=False),
        sa.Column("analytics", sa.JSON(), nullable=False),
        sa.Column("insights", sa.JSON(), nullable=False),
        sa.Column("graph_payload", sa.JSON(), nullable=False),
        sa.Column("generated_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["generated_by_user_id"],
            ["users.id"],
            name=op.f("fk_graph_snapshots_generated_by_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_graph_snapshots")),
    )
    op.create_index(op.f("ix_graph_snapshots_generated_by_user_id"), "graph_snapshots", ["generated_by_user_id"])
    op.create_index(op.f("ix_graph_snapshots_name"), "graph_snapshots", ["name"])
    op.create_index(op.f("ix_graph_snapshots_snapshot_type"), "graph_snapshots", ["snapshot_type"])

    op.create_table(
        "graph_edges",
        sa.Column("stable_key", sa.String(length=64), nullable=False),
        sa.Column("source_node_id", sa.String(length=36), nullable=False),
        sa.Column("target_node_id", sa.String(length=36), nullable=False),
        sa.Column("relationship_type", sa.String(length=80), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("is_bidirectional", sa.Boolean(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["source_node_id"],
            ["graph_nodes.id"],
            name=op.f("fk_graph_edges_source_node_id_graph_nodes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_node_id"],
            ["graph_nodes.id"],
            name=op.f("fk_graph_edges_target_node_id_graph_nodes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_graph_edges")),
        sa.UniqueConstraint("stable_key", name="uq_graph_edges_stable_key"),
    )
    op.create_index(op.f("ix_graph_edges_confidence_score"), "graph_edges", ["confidence_score"])
    op.create_index(op.f("ix_graph_edges_relationship_type"), "graph_edges", ["relationship_type"])
    op.create_index(op.f("ix_graph_edges_source_node_id"), "graph_edges", ["source_node_id"])
    op.create_index(op.f("ix_graph_edges_stable_key"), "graph_edges", ["stable_key"])
    op.create_index(op.f("ix_graph_edges_target_node_id"), "graph_edges", ["target_node_id"])
    op.create_index(op.f("ix_graph_edges_weight"), "graph_edges", ["weight"])

    op.create_table(
        "node_metadata",
        sa.Column("node_id", sa.String(length=36), nullable=False),
        sa.Column("metadata_key", sa.String(length=120), nullable=False),
        sa.Column("metadata_value", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(length=40), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["node_id"],
            ["graph_nodes.id"],
            name=op.f("fk_node_metadata_node_id_graph_nodes"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_node_metadata")),
        sa.UniqueConstraint("node_id", "metadata_key", name="uq_node_metadata_node_key"),
    )
    op.create_index(op.f("ix_node_metadata_metadata_key"), "node_metadata", ["metadata_key"])
    op.create_index(op.f("ix_node_metadata_node_id"), "node_metadata", ["node_id"])

    op.create_table(
        "relationship_metadata",
        sa.Column("edge_id", sa.String(length=36), nullable=False),
        sa.Column("metadata_key", sa.String(length=120), nullable=False),
        sa.Column("metadata_value", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(length=40), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["edge_id"],
            ["graph_edges.id"],
            name=op.f("fk_relationship_metadata_edge_id_graph_edges"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_relationship_metadata")),
        sa.UniqueConstraint("edge_id", "metadata_key", name="uq_relationship_metadata_edge_key"),
    )
    op.create_index(op.f("ix_relationship_metadata_edge_id"), "relationship_metadata", ["edge_id"])
    op.create_index(op.f("ix_relationship_metadata_metadata_key"), "relationship_metadata", ["metadata_key"])


def downgrade() -> None:
    op.drop_index(op.f("ix_relationship_metadata_metadata_key"), table_name="relationship_metadata")
    op.drop_index(op.f("ix_relationship_metadata_edge_id"), table_name="relationship_metadata")
    op.drop_table("relationship_metadata")

    op.drop_index(op.f("ix_node_metadata_node_id"), table_name="node_metadata")
    op.drop_index(op.f("ix_node_metadata_metadata_key"), table_name="node_metadata")
    op.drop_table("node_metadata")

    op.drop_index(op.f("ix_graph_edges_weight"), table_name="graph_edges")
    op.drop_index(op.f("ix_graph_edges_target_node_id"), table_name="graph_edges")
    op.drop_index(op.f("ix_graph_edges_stable_key"), table_name="graph_edges")
    op.drop_index(op.f("ix_graph_edges_source_node_id"), table_name="graph_edges")
    op.drop_index(op.f("ix_graph_edges_relationship_type"), table_name="graph_edges")
    op.drop_index(op.f("ix_graph_edges_confidence_score"), table_name="graph_edges")
    op.drop_table("graph_edges")

    op.drop_index(op.f("ix_graph_snapshots_snapshot_type"), table_name="graph_snapshots")
    op.drop_index(op.f("ix_graph_snapshots_name"), table_name="graph_snapshots")
    op.drop_index(op.f("ix_graph_snapshots_generated_by_user_id"), table_name="graph_snapshots")
    op.drop_table("graph_snapshots")

    op.drop_index(op.f("ix_graph_layouts_layout_name"), table_name="graph_layouts")
    op.drop_index(op.f("ix_graph_layouts_is_default"), table_name="graph_layouts")
    op.drop_index(op.f("ix_graph_layouts_algorithm"), table_name="graph_layouts")
    op.drop_table("graph_layouts")

    op.drop_index(op.f("ix_graph_nodes_stable_key"), table_name="graph_nodes")
    op.drop_index(op.f("ix_graph_nodes_node_type"), table_name="graph_nodes")
    op.drop_index(op.f("ix_graph_nodes_name"), table_name="graph_nodes")
    op.drop_index(op.f("ix_graph_nodes_label"), table_name="graph_nodes")
    op.drop_index(op.f("ix_graph_nodes_is_collapsed"), table_name="graph_nodes")
    op.drop_index(op.f("ix_graph_nodes_importance_score"), table_name="graph_nodes")
    op.drop_index(op.f("ix_graph_nodes_document_id"), table_name="graph_nodes")
    op.drop_index(op.f("ix_graph_nodes_cluster_id"), table_name="graph_nodes")
    op.drop_table("graph_nodes")
