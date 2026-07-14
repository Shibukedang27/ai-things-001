from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_permissions
from backend.dependencies.database import get_db
from backend.models.document import Document, DocumentConcept, DocumentKeyword, DocumentSummary, DocumentTechnology
from backend.models.user import User
from backend.schemas.document import (
    DocumentConceptRead,
    DocumentKeywordRead,
    DocumentListItem,
    DocumentMetadataRead,
    DocumentRead,
    DocumentSummaryRead,
    DocumentTechnologyRead,
)
from backend.services.document_service import DocumentService

router = APIRouter()


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED, summary="Upload a document")
def upload_document(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("documents:write"))],
    file: Annotated[UploadFile | None, File()] = None,
    source_text: Annotated[str | None, Form(min_length=10)] = None,
    source_url: Annotated[str | None, Form()] = None,
    source_type: Annotated[str | None, Form()] = None,
    title: Annotated[str | None, Form(max_length=240)] = None,
    author: Annotated[str | None, Form(max_length=160)] = None,
    category: Annotated[str | None, Form(max_length=120)] = None,
) -> Document:
    file_content = file.file.read() if file is not None else None
    return DocumentService(session).ingest_document(
        current_user=current_user,
        file_content=file_content,
        filename=file.filename if file is not None else None,
        mime_type=file.content_type if file is not None else None,
        source_text=source_text,
        source_url=source_url,
        source_type=source_type,
        title=title,
        author=author,
        category=category,
    )


@router.get("", response_model=list[DocumentListItem], summary="Get documents")
def get_documents(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("documents:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[Document]:
    return DocumentService(session).list_documents(offset=offset, limit=limit)


@router.get("/{document_id}", response_model=DocumentRead, summary="Get a document")
def get_document(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("documents:read"))],
) -> Document:
    return DocumentService(session).get_document(document_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document")
def delete_document(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("documents:delete"))],
) -> Response:
    DocumentService(session).delete_document(document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{document_id}/summary", response_model=list[DocumentSummaryRead], summary="Get document summaries")
def get_summary(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("documents:read"))],
    summary_type: str | None = Query(
        default=None,
        pattern="^(executive|beginner|technical|detailed|one_minute|five_minute)$",
    ),
) -> list[DocumentSummary]:
    return DocumentService(session).get_summary(document_id, summary_type)


@router.get("/{document_id}/concepts", response_model=list[DocumentConceptRead], summary="Get document concepts")
def get_concepts(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("documents:read"))],
) -> list[DocumentConcept]:
    return DocumentService(session).get_document(document_id).concepts


@router.get("/{document_id}/keywords", response_model=list[DocumentKeywordRead], summary="Get document keywords")
def get_keywords(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("documents:read"))],
) -> list[DocumentKeyword]:
    return DocumentService(session).get_document(document_id).keywords


@router.get(
    "/{document_id}/technologies",
    response_model=list[DocumentTechnologyRead],
    summary="Get document technologies",
)
def get_technologies(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("documents:read"))],
) -> list[DocumentTechnology]:
    return DocumentService(session).get_document(document_id).technologies


@router.get("/{document_id}/metadata", response_model=DocumentMetadataRead, summary="Get document metadata")
def get_metadata(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("documents:read"))],
) -> DocumentMetadataRead:
    document = DocumentService(session).get_document(document_id)
    return DocumentMetadataRead(
        id=document.id,
        title=document.title,
        author=document.author,
        category=document.category,
        topics=document.topics,
        keywords=[keyword.value for keyword in document.keywords],
        technologies=[technology.name for technology in document.technologies],
        difficulty=document.difficulty,
        estimated_reading_time_minutes=document.estimated_reading_time_minutes,
        word_count=document.word_count,
        character_count=document.character_count,
        language=document.language,
        source_type=document.source_type,
        content_hash=document.content_hash,
        learning_objectives=document.learning_objectives,
        definitions_count=len(document.definitions),
        algorithms_count=len(document.algorithms),
        equations_count=len(document.equations),
        code_snippets_count=len(document.code_snippets),
        references_count=len(document.references),
        concepts_count=len(document.concepts),
        created_at=document.created_at,
        updated_at=document.updated_at,
    )
