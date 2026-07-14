from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from backend.models.retrieval import (
    CitationHistory,
    KnowledgeCache,
    ReasoningLog,
    RetrievalEmbedding,
    RetrievalHistory,
    RetrievalQuery,
)
from backend.repositories.base import BaseRepository


class RetrievalEmbeddingRepository(BaseRepository[RetrievalEmbedding]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RetrievalEmbedding)

    def list_by_namespace(self, *, namespace: str, collection_name: str) -> Sequence[RetrievalEmbedding]:
        statement = (
            select(RetrievalEmbedding)
            .where(RetrievalEmbedding.namespace == namespace)
            .where(RetrievalEmbedding.collection_name == collection_name)
        )
        return self.session.scalars(statement).all()

    def delete_by_document(self, document_id: str) -> None:
        self.session.execute(delete(RetrievalEmbedding).where(RetrievalEmbedding.document_id == document_id))
        self.session.flush()


class RetrievalQueryRepository(BaseRepository[RetrievalQuery]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RetrievalQuery)


class RetrievalHistoryRepository(BaseRepository[RetrievalHistory]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RetrievalHistory)

    def get_full(self, history_id: str) -> RetrievalHistory | None:
        statement = (
            select(RetrievalHistory)
            .where(RetrievalHistory.id == history_id)
            .options(
                selectinload(RetrievalHistory.query),
                selectinload(RetrievalHistory.reasoning_logs),
                selectinload(RetrievalHistory.citations),
            )
        )
        return self.session.scalars(statement).first()

    def list_history(self, *, offset: int = 0, limit: int = 50) -> Sequence[RetrievalHistory]:
        statement = (
            select(RetrievalHistory)
            .options(
                selectinload(RetrievalHistory.query),
                selectinload(RetrievalHistory.reasoning_logs),
                selectinload(RetrievalHistory.citations),
            )
            .order_by(RetrievalHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()


class KnowledgeCacheRepository(BaseRepository[KnowledgeCache]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, KnowledgeCache)

    def get_by_key(self, cache_key: str) -> KnowledgeCache | None:
        statement = select(KnowledgeCache).where(KnowledgeCache.cache_key == cache_key)
        return self.session.scalars(statement).first()


class CitationHistoryRepository(BaseRepository[CitationHistory]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, CitationHistory)

    def list_by_history(self, history_id: str) -> Sequence[CitationHistory]:
        statement = (
            select(CitationHistory)
            .where(CitationHistory.retrieval_history_id == history_id)
            .order_by(CitationHistory.citation_key.asc())
        )
        return self.session.scalars(statement).all()


class ReasoningLogRepository(BaseRepository[ReasoningLog]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, ReasoningLog)


__all__ = [
    "CitationHistory",
    "CitationHistoryRepository",
    "KnowledgeCache",
    "KnowledgeCacheRepository",
    "ReasoningLog",
    "ReasoningLogRepository",
    "RetrievalEmbedding",
    "RetrievalEmbeddingRepository",
    "RetrievalHistory",
    "RetrievalHistoryRepository",
    "RetrievalQuery",
    "RetrievalQueryRepository",
]
