from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.document import (
    Document,
    DocumentChunk,
    DocumentConcept,
    DocumentEmbedding,
    DocumentKeyword,
    DocumentReference,
    DocumentSummary,
    DocumentTechnology,
    KnowledgeRelationship,
)
from backend.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Document)

    def get_full(self, document_id: str) -> Document | None:
        statement = select(Document).where(Document.id == document_id).options(*self._load_options())
        return self.session.scalars(statement).first()

    def get_by_hash(self, content_hash: str) -> Document | None:
        statement = select(Document).where(Document.content_hash == content_hash).options(*self._load_options())
        return self.session.scalars(statement).first()

    def list_documents(self, *, offset: int = 0, limit: int = 50) -> Sequence[Document]:
        statement = (
            select(Document)
            .options(
                selectinload(Document.keywords),
                selectinload(Document.technologies),
                selectinload(Document.summaries),
            )
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def _load_options(self) -> tuple[object, ...]:
        return (
            selectinload(Document.chunks).selectinload(DocumentChunk.embeddings),
            selectinload(Document.summaries),
            selectinload(Document.concepts),
            selectinload(Document.keywords),
            selectinload(Document.technologies),
            selectinload(Document.embeddings).selectinload(DocumentEmbedding.chunk),
            selectinload(Document.references),
            selectinload(Document.relationships),
        )


__all__ = [
    "Document",
    "DocumentChunk",
    "DocumentConcept",
    "DocumentEmbedding",
    "DocumentKeyword",
    "DocumentReference",
    "DocumentRepository",
    "DocumentSummary",
    "DocumentTechnology",
    "KnowledgeRelationship",
]
