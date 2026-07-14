from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_permissions
from backend.dependencies.database import get_db
from backend.models.knowledge_dna import KnowledgeDNA, LearningPath, Prerequisite
from backend.models.user import User
from backend.schemas.common import MessageResponse
from backend.schemas.knowledge_dna import (
    KnowledgeDNARead,
    KnowledgeDNAUpdate,
    LearningPathRead,
    PrerequisiteRead,
    RelatedTopicRead,
)
from backend.services.knowledge_dna_service import KnowledgeDNAService

router = APIRouter()


@router.post(
    "/documents/{document_id}/generate",
    response_model=KnowledgeDNARead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Knowledge DNA",
)
def generate_knowledge_dna(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("knowledge_dna:write"))],
) -> KnowledgeDNA:
    return KnowledgeDNAService(session).generate_for_document(document_id)


@router.get("/documents/{document_id}", response_model=KnowledgeDNARead, summary="Get Knowledge DNA by document")
def get_knowledge_dna_for_document(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("knowledge_dna:read"))],
) -> KnowledgeDNA:
    return KnowledgeDNAService(session).get_by_document(document_id)


@router.get("/{dna_id}", response_model=KnowledgeDNARead, summary="Get Knowledge DNA")
def get_knowledge_dna(
    dna_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("knowledge_dna:read"))],
) -> KnowledgeDNA:
    return KnowledgeDNAService(session).get(dna_id)


@router.patch("/{dna_id}", response_model=KnowledgeDNARead, summary="Update Knowledge DNA")
def update_knowledge_dna(
    dna_id: str,
    payload: KnowledgeDNAUpdate,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("knowledge_dna:write"))],
) -> KnowledgeDNA:
    return KnowledgeDNAService(session).update(dna_id, payload)


@router.delete("/{dna_id}", response_model=MessageResponse, summary="Delete Knowledge DNA")
def delete_knowledge_dna(
    dna_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("knowledge_dna:delete"))],
) -> MessageResponse:
    KnowledgeDNAService(session).delete(dna_id)
    return MessageResponse(message="Knowledge DNA deleted.")


@router.get(
    "/documents/{document_id}/learning-path",
    response_model=list[LearningPathRead],
    summary="Get Learning Path",
)
def get_learning_path(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("knowledge_dna:read"))],
) -> list[LearningPath]:
    return KnowledgeDNAService(session).learning_path(document_id)


@router.get(
    "/documents/{document_id}/related-topics",
    response_model=list[RelatedTopicRead],
    summary="Get Related Topics",
)
def get_related_topics(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("knowledge_dna:read"))],
) -> list[RelatedTopicRead]:
    return KnowledgeDNAService(session).related_topics(document_id)


@router.get(
    "/documents/{document_id}/prerequisites",
    response_model=list[PrerequisiteRead],
    summary="Get Prerequisites",
)
def get_prerequisites(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("knowledge_dna:read"))],
) -> list[Prerequisite]:
    return KnowledgeDNAService(session).prerequisites(document_id)
