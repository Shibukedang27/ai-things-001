import json
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from retrieval.types import SearchMode
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_permissions
from backend.dependencies.database import get_db
from backend.models.user import User
from backend.schemas.retrieval import (
    AskQuestionRequest,
    CitationViewerResponse,
    ReasoningHistoryItem,
    RelatedConceptsResponse,
    RetrievalAnswerRead,
    RetrievalRequest,
    SearchResponse,
)
from backend.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post(
    "/ask",
    response_model=RetrievalAnswerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ask Question",
)
def ask_question(
    payload: AskQuestionRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("retrieval:write"))],
) -> RetrievalAnswerRead:
    return RetrievalService(session).ask_question(payload, current_user)


@router.post("/ask/stream", summary="Ask Question With Streaming Response")
def ask_question_stream(
    payload: AskQuestionRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("retrieval:write"))],
) -> StreamingResponse:
    result = RetrievalService(session).ask_question(payload, current_user)

    def _events() -> Iterator[str]:
        yield json.dumps({"event": "metadata", "history_id": result.history_id, "confidence": result.confidence_score})
        yield "\n"
        yield json.dumps({"event": "answer", "content": result.answer})
        yield "\n"
        yield json.dumps({"event": "citations", "citations": [citation.model_dump() for citation in result.citations]})
        yield "\n"

    return StreamingResponse(_events(), media_type="application/x-ndjson")


@router.post("/search/hybrid", response_model=SearchResponse, summary="Hybrid Search")
def hybrid_search(
    payload: RetrievalRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("retrieval:read"))],
) -> SearchResponse:
    return RetrievalService(session).search(payload, current_user, mode=SearchMode.HYBRID)


@router.post("/search/semantic", response_model=SearchResponse, summary="Semantic Search")
def semantic_search(
    payload: RetrievalRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("retrieval:read"))],
) -> SearchResponse:
    return RetrievalService(session).search(payload, current_user, mode=SearchMode.SEMANTIC)


@router.post("/search/keyword", response_model=SearchResponse, summary="Keyword Search")
def keyword_search(
    payload: RetrievalRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("retrieval:read"))],
) -> SearchResponse:
    return RetrievalService(session).search(payload, current_user, mode=SearchMode.KEYWORD)


@router.post("/related-concepts", response_model=RelatedConceptsResponse, summary="Related Concepts")
def related_concepts(
    payload: RetrievalRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("retrieval:read"))],
) -> RelatedConceptsResponse:
    return RetrievalService(session).related_concepts(payload, current_user)


@router.get("/history", response_model=list[ReasoningHistoryItem], summary="Reasoning History")
def reasoning_history(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("retrieval:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ReasoningHistoryItem]:
    return RetrievalService(session).reasoning_history(offset=offset, limit=limit)


@router.get("/citations/{history_id}", response_model=CitationViewerResponse, summary="Citation Viewer")
def citation_viewer(
    history_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("retrieval:read"))],
) -> CitationViewerResponse:
    return RetrievalService(session).citation_viewer(history_id)
