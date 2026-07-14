from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.knowledge_dna import (
    KnowledgeDNA,
    KnowledgeEdge,
    KnowledgeHierarchy,
    KnowledgeNode,
    LearningPath,
    Prerequisite,
    RelatedDocument,
)
from backend.repositories.base import BaseRepository


class KnowledgeDNARepository(BaseRepository[KnowledgeDNA]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, KnowledgeDNA)

    def get_full(self, dna_id: str) -> KnowledgeDNA | None:
        statement = select(KnowledgeDNA).where(KnowledgeDNA.id == dna_id).options(*self._load_options())
        return self.session.scalars(statement).first()

    def get_by_document_id(self, document_id: str) -> KnowledgeDNA | None:
        statement = select(KnowledgeDNA).where(KnowledgeDNA.document_id == document_id).options(*self._load_options())
        return self.session.scalars(statement).first()

    def _load_options(self) -> tuple[object, ...]:
        return (
            selectinload(KnowledgeDNA.nodes),
            selectinload(KnowledgeDNA.edges),
            selectinload(KnowledgeDNA.hierarchy_items),
            selectinload(KnowledgeDNA.learning_path_steps),
            selectinload(KnowledgeDNA.prerequisite_items),
            selectinload(KnowledgeDNA.related_documents),
        )


__all__ = [
    "KnowledgeDNA",
    "KnowledgeDNARepository",
    "KnowledgeEdge",
    "KnowledgeHierarchy",
    "KnowledgeNode",
    "LearningPath",
    "Prerequisite",
    "RelatedDocument",
]
