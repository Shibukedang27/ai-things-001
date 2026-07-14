from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.document import Document


class KnowledgeDNA(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_dna"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), unique=True, index=True)
    document_title: Mapped[str] = mapped_column(String(240), index=True, nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    estimated_reading_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    knowledge_score: Mapped[float] = mapped_column(Float, nullable=False)
    interview_importance: Mapped[float] = mapped_column(Float, nullable=False)
    industry_relevance: Mapped[float] = mapped_column(Float, nullable=False)
    implementation_complexity: Mapped[float] = mapped_column(Float, nullable=False)
    research_category: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    primary_concepts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    secondary_concepts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    prerequisites: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    advanced_topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    future_learning_topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    technologies_used: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    programming_languages: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    frameworks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    libraries: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    algorithms: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    datasets: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    research_papers: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    learning_order: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    estimated_mastery_time_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    mathematical_topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    parent_topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    child_topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    sibling_topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    knowledge_chains: Mapped[list[list[str]]] = mapped_column(JSON, default=list, nullable=False)
    research_evolution: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    document: Mapped[Document] = relationship("Document")
    nodes: Mapped[list[KnowledgeNode]] = relationship(
        "KnowledgeNode",
        back_populates="knowledge_dna",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    edges: Mapped[list[KnowledgeEdge]] = relationship(
        "KnowledgeEdge",
        back_populates="knowledge_dna",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    hierarchy_items: Mapped[list[KnowledgeHierarchy]] = relationship(
        "KnowledgeHierarchy",
        back_populates="knowledge_dna",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    learning_path_steps: Mapped[list[LearningPath]] = relationship(
        "LearningPath",
        back_populates="knowledge_dna",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    prerequisite_items: Mapped[list[Prerequisite]] = relationship(
        "Prerequisite",
        back_populates="knowledge_dna",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    related_documents: Mapped[list[RelatedDocument]] = relationship(
        "RelatedDocument",
        back_populates="knowledge_dna",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class KnowledgeNode(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_nodes"
    __table_args__ = (UniqueConstraint("knowledge_dna_id", "stable_key", name="uq_knowledge_nodes_dna_key"),)

    knowledge_dna_id: Mapped[str] = mapped_column(ForeignKey("knowledge_dna.id", ondelete="CASCADE"), index=True)
    stable_key: Mapped[str] = mapped_column(String(240), index=True, nullable=False)
    node_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(240), index=True, nullable=False)
    label: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance_score: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    knowledge_dna: Mapped[KnowledgeDNA] = relationship("KnowledgeDNA", back_populates="nodes")


class KnowledgeEdge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_edges"

    knowledge_dna_id: Mapped[str] = mapped_column(ForeignKey("knowledge_dna.id", ondelete="CASCADE"), index=True)
    source_node_id: Mapped[str | None] = mapped_column(
        ForeignKey("knowledge_nodes.id", ondelete="SET NULL"),
        index=True,
    )
    target_node_id: Mapped[str | None] = mapped_column(
        ForeignKey("knowledge_nodes.id", ondelete="SET NULL"),
        index=True,
    )
    source_key: Mapped[str] = mapped_column(String(240), index=True, nullable=False)
    target_key: Mapped[str] = mapped_column(String(240), index=True, nullable=False)
    edge_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    knowledge_dna: Mapped[KnowledgeDNA] = relationship("KnowledgeDNA", back_populates="edges")


class KnowledgeHierarchy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_hierarchy"

    knowledge_dna_id: Mapped[str] = mapped_column(ForeignKey("knowledge_dna.id", ondelete="CASCADE"), index=True)
    parent_topic: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    child_topic: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    hierarchy_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)

    knowledge_dna: Mapped[KnowledgeDNA] = relationship("KnowledgeDNA", back_populates="hierarchy_items")


class LearningPath(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "learning_path"
    __table_args__ = (UniqueConstraint("knowledge_dna_id", "order_index", name="uq_learning_path_dna_order"),)

    knowledge_dna_id: Mapped[str] = mapped_column(ForeignKey("knowledge_dna.id", ondelete="CASCADE"), index=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    resource_hint: Mapped[str] = mapped_column(Text, nullable=False)

    knowledge_dna: Mapped[KnowledgeDNA] = relationship("KnowledgeDNA", back_populates="learning_path_steps")


class Prerequisite(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prerequisites"

    knowledge_dna_id: Mapped[str] = mapped_column(ForeignKey("knowledge_dna.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    prerequisite_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    importance_score: Mapped[float] = mapped_column(Float, nullable=False)
    source_concept: Mapped[str | None] = mapped_column(String(180), nullable=True)

    knowledge_dna: Mapped[KnowledgeDNA] = relationship("KnowledgeDNA", back_populates="prerequisite_items")


class RelatedDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "related_documents"
    __table_args__ = (
        UniqueConstraint("knowledge_dna_id", "related_document_id", name="uq_related_documents_dna_document"),
    )

    knowledge_dna_id: Mapped[str] = mapped_column(ForeignKey("knowledge_dna.id", ondelete="CASCADE"), index=True)
    related_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    shared_signals: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    relationship_reason: Mapped[str] = mapped_column(Text, nullable=False)

    knowledge_dna: Mapped[KnowledgeDNA] = relationship("KnowledgeDNA", back_populates="related_documents")
    related_document: Mapped[Document] = relationship("Document")
