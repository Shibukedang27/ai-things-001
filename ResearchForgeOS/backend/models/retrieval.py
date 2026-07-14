from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.models.document import Document, DocumentChunk
    from backend.models.user import User


class RetrievalEmbedding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "retrieval_embeddings"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    chunk_id: Mapped[str | None] = mapped_column(ForeignKey("document_chunks.id", ondelete="CASCADE"), index=True)
    namespace: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    collection_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    vector_store_backend: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    embedding_dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    vector: Mapped[list[float]] = mapped_column(JSON, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    cache_key: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    document: Mapped[Document] = relationship("Document")
    chunk: Mapped[DocumentChunk | None] = relationship("DocumentChunk")


class RetrievalQuery(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "retrieval_queries"

    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_query: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    query_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    intent: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    expanded_queries: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    filters: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    requested_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)

    requested_by: Mapped[User | None] = relationship("User")
    histories: Mapped[list[RetrievalHistory]] = relationship(
        "RetrievalHistory",
        back_populates="query",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class RetrievalHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "retrieval_history"

    query_id: Mapped[str] = mapped_column(ForeignKey("retrieval_queries.id", ondelete="CASCADE"), index=True)
    mode: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    cache_hit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_documents: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    retrieved_sections: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    reasoning_path: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list, nullable=False)
    supporting_evidence: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    validation: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    query: Mapped[RetrievalQuery] = relationship("RetrievalQuery", back_populates="histories")
    reasoning_logs: Mapped[list[ReasoningLog]] = relationship(
        "ReasoningLog",
        back_populates="retrieval_history",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    citations: Mapped[list[CitationHistory]] = relationship(
        "CitationHistory",
        back_populates="retrieval_history",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class KnowledgeCache(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_cache"

    cache_key: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    cache_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    query_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)


class ReasoningLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reasoning_logs"

    retrieval_history_id: Mapped[str] = mapped_column(
        ForeignKey("retrieval_history.id", ondelete="CASCADE"),
        index=True,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)

    retrieval_history: Mapped[RetrievalHistory] = relationship("RetrievalHistory", back_populates="reasoning_logs")


class CitationHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "citation_history"

    retrieval_history_id: Mapped[str] = mapped_column(
        ForeignKey("retrieval_history.id", ondelete="CASCADE"),
        index=True,
    )
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"), index=True)
    chunk_id: Mapped[str | None] = mapped_column(ForeignKey("document_chunks.id", ondelete="SET NULL"), index=True)
    citation_key: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    section_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    retrieval_history: Mapped[RetrievalHistory] = relationship("RetrievalHistory", back_populates="citations")
    document: Mapped[Document | None] = relationship("Document")
    chunk: Mapped[DocumentChunk | None] = relationship("DocumentChunk")
