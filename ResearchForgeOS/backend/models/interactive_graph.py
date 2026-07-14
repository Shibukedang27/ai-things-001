from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.document import Document
    from backend.models.user import User


class GraphNode(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "graph_nodes"
    __table_args__ = (UniqueConstraint("stable_key", name="uq_graph_nodes_stable_key"),)

    stable_key: Mapped[str] = mapped_column(String(260), index=True, nullable=False)
    node_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(240), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    importance_score: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    degree: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cluster_id: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    is_collapsed: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    position_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    size: Mapped[float] = mapped_column(Float, nullable=False)
    color: Mapped[str] = mapped_column(String(24), nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    document: Mapped[Document | None] = relationship("Document")
    source_edges: Mapped[list[GraphEdge]] = relationship(
        "GraphEdge",
        foreign_keys="GraphEdge.source_node_id",
        back_populates="source_node",
    )
    target_edges: Mapped[list[GraphEdge]] = relationship(
        "GraphEdge",
        foreign_keys="GraphEdge.target_node_id",
        back_populates="target_node",
    )
    metadata_items: Mapped[list[NodeMetadata]] = relationship(
        "NodeMetadata",
        back_populates="node",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class GraphEdge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "graph_edges"
    __table_args__ = (UniqueConstraint("stable_key", name="uq_graph_edges_stable_key"),)

    stable_key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id", ondelete="CASCADE"), index=True)
    target_node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(Float, index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    is_bidirectional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    source_node: Mapped[GraphNode] = relationship(
        "GraphNode",
        foreign_keys=[source_node_id],
        back_populates="source_edges",
    )
    target_node: Mapped[GraphNode] = relationship(
        "GraphNode",
        foreign_keys=[target_node_id],
        back_populates="target_edges",
    )
    metadata_items: Mapped[list[RelationshipMetadata]] = relationship(
        "RelationshipMetadata",
        back_populates="edge",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class NodeMetadata(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "node_metadata"
    __table_args__ = (UniqueConstraint("node_id", "metadata_key", name="uq_node_metadata_node_key"),)

    node_id: Mapped[str] = mapped_column(ForeignKey("graph_nodes.id", ondelete="CASCADE"), index=True)
    metadata_key: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    metadata_value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    node: Mapped[GraphNode] = relationship("GraphNode", back_populates="metadata_items")


class RelationshipMetadata(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "relationship_metadata"
    __table_args__ = (UniqueConstraint("edge_id", "metadata_key", name="uq_relationship_metadata_edge_key"),)

    edge_id: Mapped[str] = mapped_column(ForeignKey("graph_edges.id", ondelete="CASCADE"), index=True)
    metadata_key: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    metadata_value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    edge: Mapped[GraphEdge] = relationship("GraphEdge", back_populates="metadata_items")


class GraphLayout(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "graph_layouts"

    layout_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False)
    viewport: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    positions: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)


class GraphSnapshot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "graph_snapshots"

    name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    snapshot_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    node_count: Mapped[int] = mapped_column(Integer, nullable=False)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False)
    analytics: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    insights: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    graph_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    generated_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)

    generated_by: Mapped[User | None] = relationship("User")
