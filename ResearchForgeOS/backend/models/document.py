from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.user import User


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(240), index=True, nullable=False)
    author: Mapped[str | None] = mapped_column(String(160), nullable=True)
    category: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), index=True, nullable=False, default="processed")
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="en")
    difficulty: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    estimated_reading_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    cleaned_text: Mapped[str] = mapped_column(Text, nullable=False)
    topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    definitions: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list, nullable=False)
    algorithms: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list, nullable=False)
    equations: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list, nullable=False)
    code_snippets: Mapped[list[dict[str, str]]] = mapped_column(JSON, default=list, nullable=False)
    learning_objectives: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    learning_assets: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_by: Mapped[User | None] = relationship("User")
    chunks: Mapped[list[DocumentChunk]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    summaries: Mapped[list[DocumentSummary]] = relationship(
        "DocumentSummary",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    concepts: Mapped[list[DocumentConcept]] = relationship(
        "DocumentConcept",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    keywords: Mapped[list[DocumentKeyword]] = relationship(
        "DocumentKeyword",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    technologies: Mapped[list[DocumentTechnology]] = relationship(
        "DocumentTechnology",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    embeddings: Mapped[list[DocumentEmbedding]] = relationship(
        "DocumentEmbedding",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    references: Mapped[list[DocumentReference]] = relationship(
        "DocumentReference",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    relationships: Mapped[list[KnowledgeRelationship]] = relationship(
        "KnowledgeRelationship",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DocumentChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunks_document_id_chunk_index"),
    )

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="chunks")
    embeddings: Mapped[list[DocumentEmbedding]] = relationship(
        "DocumentEmbedding",
        back_populates="chunk",
        cascade="all, delete-orphan",
    )


class DocumentSummary(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_summaries"
    __table_args__ = (UniqueConstraint("document_id", "summary_type", name="uq_document_summaries_document_id_type"),)

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    summary_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="summaries")


class DocumentConcept(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_concepts"
    __table_args__ = (UniqueConstraint("document_id", "normalized_name", name="uq_document_concepts_document_id_name"),)

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    concept_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    prerequisites: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    dependencies: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="concepts")


class DocumentKeyword(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_keywords"
    __table_args__ = (
        UniqueConstraint("document_id", "normalized_value", name="uq_document_keywords_document_id_value"),
    )

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    value: Mapped[str] = mapped_column(String(140), index=True, nullable=False)
    normalized_value: Mapped[str] = mapped_column(String(140), index=True, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="keywords")


class DocumentTechnology(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_technologies"
    __table_args__ = (
        UniqueConstraint("document_id", "normalized_name", name="uq_document_technologies_document_id_name"),
    )

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="technologies")


class DocumentEmbedding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_embeddings"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    chunk_id: Mapped[str | None] = mapped_column(ForeignKey("document_chunks.id", ondelete="CASCADE"), index=True)
    embedding_model: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    embedding_dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    vector: Mapped[list[float]] = mapped_column(JSON, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="embeddings")
    chunk: Mapped[DocumentChunk | None] = relationship("DocumentChunk", back_populates="embeddings")


class DocumentReference(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_references"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    authors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    source: Mapped[str | None] = mapped_column(String(180), nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    citation_text: Mapped[str] = mapped_column(Text, nullable=False)
    reference_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="references")


class KnowledgeRelationship(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_relationships"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    source_entity_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    source_entity_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    source_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    target_entity_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    target_entity_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    target_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    document: Mapped[Document] = relationship("Document", back_populates="relationships")
