from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_permissions
from backend.dependencies.database import get_db
from backend.models.learning import Achievement, Certificate, CodingChallenge, Flashcard, Quiz, RevisionPlan
from backend.models.user import User
from backend.schemas.learning import (
    AchievementRead,
    CertificateRead,
    CodingChallengeRead,
    FlashcardRead,
    GenerateLearningRequest,
    GenerateQuizRequest,
    GenerateRevisionPlanRequest,
    LearningBundleRead,
    LearningProgressResponse,
    QuizRead,
    ReviewFlashcardsRequest,
    ReviewFlashcardsResponse,
    RevisionPlanRead,
    StartQuizResponse,
    SubmitQuizRequest,
    SubmitQuizResponse,
)
from backend.services.learning_service import AdaptiveLearningService

router = APIRouter()


@router.post(
    "/documents/{document_id}/generate",
    response_model=LearningBundleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Adaptive Learning Assets",
)
async def generate_learning_assets(
    document_id: str,
    payload: GenerateLearningRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:write"))],
) -> LearningBundleRead:
    return AdaptiveLearningService(session).generate_bundle(document_id, current_user, force=payload.force)


@router.get(
    "/documents/{document_id}",
    response_model=LearningBundleRead,
    summary="Get Adaptive Learning Bundle",
)
async def get_learning_bundle(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
) -> LearningBundleRead:
    return AdaptiveLearningService(session).bundle_for_document(document_id, current_user)


@router.post(
    "/documents/{document_id}/flashcards/generate",
    response_model=list[FlashcardRead],
    status_code=status.HTTP_201_CREATED,
    summary="Generate Flashcards",
)
async def generate_flashcards(
    document_id: str,
    payload: GenerateLearningRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:write"))],
) -> list[Flashcard]:
    return AdaptiveLearningService(session).generate_flashcards(document_id, current_user, force=payload.force)


@router.get(
    "/documents/{document_id}/flashcards",
    response_model=list[FlashcardRead],
    summary="Get Flashcards",
)
async def get_flashcards(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
) -> list[Flashcard]:
    return AdaptiveLearningService(session).list_flashcards(document_id, current_user)


@router.post(
    "/documents/{document_id}/quizzes/generate",
    response_model=QuizRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Adaptive Quiz",
)
async def generate_quiz(
    document_id: str,
    payload: GenerateQuizRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:write"))],
) -> Quiz:
    return AdaptiveLearningService(session).generate_quiz(document_id, payload, current_user)


@router.get(
    "/documents/{document_id}/quizzes",
    response_model=list[QuizRead],
    summary="Get Quizzes",
)
async def get_quizzes(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
) -> list[Quiz]:
    return AdaptiveLearningService(session).list_quizzes(document_id, current_user)


@router.post(
    "/quizzes/{quiz_id}/start",
    response_model=StartQuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start Quiz",
)
async def start_quiz(
    quiz_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:write"))],
) -> StartQuizResponse:
    return AdaptiveLearningService(session).start_quiz(quiz_id, current_user)


@router.post(
    "/quiz-attempts/{attempt_id}/submit",
    response_model=SubmitQuizResponse,
    summary="Submit Quiz",
)
async def submit_quiz(
    attempt_id: str,
    payload: SubmitQuizRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:write"))],
) -> SubmitQuizResponse:
    return AdaptiveLearningService(session).submit_quiz(attempt_id, payload, current_user)


@router.post(
    "/flashcards/review",
    response_model=ReviewFlashcardsResponse,
    summary="Review Flashcards",
)
async def review_flashcards(
    payload: ReviewFlashcardsRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:write"))],
) -> ReviewFlashcardsResponse:
    return AdaptiveLearningService(session).review_flashcards(payload, current_user)


@router.get(
    "/progress",
    response_model=LearningProgressResponse,
    summary="Get Learning Progress",
)
async def get_learning_progress(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
    document_id: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> LearningProgressResponse:
    return AdaptiveLearningService(session).progress_for_user(
        current_user,
        document_id=document_id,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/achievements",
    response_model=list[AchievementRead],
    summary="Get Achievements",
)
async def get_achievements(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[Achievement]:
    return AdaptiveLearningService(session).list_achievements(current_user, offset=offset, limit=limit)


@router.get(
    "/certificates",
    response_model=list[CertificateRead],
    summary="Get Certificates",
)
async def get_certificates(
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[Certificate]:
    return AdaptiveLearningService(session).list_certificates(current_user, offset=offset, limit=limit)


@router.post(
    "/documents/{document_id}/revision-plan",
    response_model=RevisionPlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Revision Plan",
)
async def generate_revision_plan(
    document_id: str,
    payload: GenerateRevisionPlanRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:write"))],
) -> RevisionPlan:
    return AdaptiveLearningService(session).generate_revision_plan(document_id, payload, current_user)


@router.get(
    "/documents/{document_id}/revision-plans",
    response_model=list[RevisionPlanRead],
    summary="Get Revision Plans",
)
async def get_revision_plans(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
) -> list[RevisionPlan]:
    return AdaptiveLearningService(session).list_revision_plans(document_id, current_user)


@router.get(
    "/documents/{document_id}/coding-challenges",
    response_model=list[CodingChallengeRead],
    summary="Get Coding Challenges",
)
async def get_coding_challenges(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
) -> list[CodingChallenge]:
    return AdaptiveLearningService(session).list_coding_challenges(document_id, current_user)


@router.get(
    "/documents/{document_id}/interview-questions",
    response_model=list[dict[str, object]],
    summary="Get Interview Preparation Questions",
)
async def get_interview_questions(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("learning:read"))],
) -> list[dict[str, object]]:
    return AdaptiveLearningService(session).interview_questions(document_id, current_user)
