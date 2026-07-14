from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import timedelta
from typing import Any

from adaptive_learning import AdaptiveLearningEngine, SpacedRepetitionScheduler
from adaptive_learning.achievements import AchievementEngine
from adaptive_learning.quizzes import QuizEngine
from adaptive_learning.revision import RevisionEngine
from adaptive_learning.types import (
    AchievementDraft,
    AdaptiveLearningBundle,
    CardDifficulty,
    CodingChallengeDraft,
    FlashcardDraft,
    InterviewQuestionDraft,
    LearningConcept,
    LearningSource,
    MemoryState,
    QuizDraft,
    RevisionPlanDraft,
)
from adaptive_learning.utils import excerpt_for, stable_hash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.exceptions import ConflictError, NotFoundError, ValidationError
from backend.models.document import Document
from backend.models.learning import (
    Achievement,
    Certificate,
    CodingChallenge,
    Flashcard,
    LearningSession,
    MemoryTracking,
    Progress,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    Review,
    RevisionPlan,
)
from backend.models.user import User
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.learning_repository import (
    AchievementRepository,
    CertificateRepository,
    CodingChallengeRepository,
    FlashcardRepository,
    LearningSessionRepository,
    MemoryTrackingRepository,
    ProgressRepository,
    QuizAttemptRepository,
    QuizRepository,
    ReviewRepository,
    RevisionPlanRepository,
)
from backend.schemas.learning import (
    GenerateQuizRequest,
    GenerateRevisionPlanRequest,
    LearningBundleRead,
    LearningProgressResponse,
    ReviewFlashcardsRequest,
    ReviewFlashcardsResponse,
    StartQuizResponse,
    SubmitQuizRequest,
    SubmitQuizResponse,
)
from backend.services.learning_background_service import LearningBackgroundService
from backend.utils.datetime import utc_now

logger = logging.getLogger(__name__)


class AdaptiveLearningService:
    def __init__(
        self,
        session: Session,
        engine: AdaptiveLearningEngine | None = None,
        scheduler: SpacedRepetitionScheduler | None = None,
        quiz_engine: QuizEngine | None = None,
        revision_engine: RevisionEngine | None = None,
        achievement_engine: AchievementEngine | None = None,
        background: LearningBackgroundService | None = None,
    ) -> None:
        self.session = session
        self.engine = engine or AdaptiveLearningEngine()
        self.scheduler = scheduler or SpacedRepetitionScheduler()
        self.quiz_engine = quiz_engine or QuizEngine()
        self.revision_engine = revision_engine or RevisionEngine()
        self.achievement_engine = achievement_engine or AchievementEngine()
        self.background = background or LearningBackgroundService(self.scheduler)
        self.documents = DocumentRepository(session)
        self.flashcards = FlashcardRepository(session)
        self.quizzes = QuizRepository(session)
        self.attempts = QuizAttemptRepository(session)
        self.reviews = ReviewRepository(session)
        self.sessions = LearningSessionRepository(session)
        self.achievements = AchievementRepository(session)
        self.certificates = CertificateRepository(session)
        self.memory = MemoryTrackingRepository(session)
        self.progress = ProgressRepository(session)
        self.coding_challenges = CodingChallengeRepository(session)
        self.revision_plans = RevisionPlanRepository(session)

    def sync_document_learning(
        self,
        document: Document,
        current_user: User,
        *,
        force: bool = False,
        commit: bool = True,
    ) -> LearningBundleRead:
        existing = self.flashcards.list_by_document(owner_user_id=current_user.id, document_id=document.id, limit=1)
        if existing and not force:
            bundle = self.bundle_for_document(document.id, current_user)
            if commit:
                self.session.commit()
            return bundle

        if force:
            self._delete_document_learning(document.id, current_user.id)

        source = self._source_from_document(document)
        bundle = self.engine.build(source)
        flashcards = self._persist_flashcards(document, current_user, bundle.flashcards)
        quiz = self._persist_quiz(document, current_user, bundle.quiz, bundle.interview_questions)
        coding_challenges = self._persist_coding_challenges(document, current_user, bundle.coding_challenges)
        revision_plans = self._persist_revision_plans(document, current_user, bundle.revision_plans)
        progress = self._persist_progress(document, current_user, bundle, flashcards, quiz, coding_challenges)
        achievements = self._persist_achievements(current_user, bundle.achievements)
        now = utc_now()
        self.sessions.add(
            LearningSession(
                owner_user_id=current_user.id,
                document_id=document.id,
                session_type="generation",
                title=f"{document.title} adaptive learning generated",
                status="completed",
                started_at=now,
                ended_at=now,
                duration_seconds=0,
                items_studied=len(flashcards) + len(quiz.questions) + len(coding_challenges),
                correct_count=0,
                total_count=len(flashcards) + len(quiz.questions) + len(coding_challenges),
                mastery_delta=0.0,
                metadata_json={"engine": "adaptive_learning_v1", "revision_plan_count": len(revision_plans)},
            )
        )
        self._refresh_progress(document, current_user, source=source, progress=progress)
        if commit:
            self.session.commit()
        logger.info(
            "Adaptive learning bundle generated",
            extra={"document_id": document.id, "user_id": current_user.id},
        )
        return self._bundle_response(document.id, current_user, achievements=achievements)

    def generate_bundle(self, document_id: str, current_user: User, *, force: bool = False) -> LearningBundleRead:
        document = self._get_document(document_id)
        return self.sync_document_learning(document, current_user, force=force)

    def bundle_for_document(self, document_id: str, current_user: User) -> LearningBundleRead:
        document = self._get_document(document_id)
        quiz = self._latest_quiz(document.id, current_user.id)
        if quiz is None:
            return self.sync_document_learning(document, current_user)
        progress = self._get_or_create_progress(document, current_user, self._source_from_document(document))
        return self._bundle_response(document.id, current_user, progress=progress)

    def generate_flashcards(self, document_id: str, current_user: User, *, force: bool = False) -> list[Flashcard]:
        document = self._get_document(document_id)
        self.sync_document_learning(document, current_user, force=force, commit=False)
        self.session.commit()
        return list(self.flashcards.list_by_document(owner_user_id=current_user.id, document_id=document.id, limit=500))

    def list_flashcards(self, document_id: str, current_user: User) -> list[Flashcard]:
        document = self._get_document(document_id)
        existing = list(
            self.flashcards.list_by_document(
                owner_user_id=current_user.id,
                document_id=document.id,
                limit=500,
            )
        )
        if existing:
            return existing
        self.sync_document_learning(document, current_user, commit=False)
        self.session.commit()
        return list(self.flashcards.list_by_document(owner_user_id=current_user.id, document_id=document.id, limit=500))

    def generate_quiz(self, document_id: str, payload: GenerateQuizRequest, current_user: User) -> Quiz:
        document = self._get_document(document_id)
        source = self._source_from_document(document)
        draft = self.quiz_engine.generate(source, difficulty=payload.difficulty, limit=payload.question_limit)
        quiz = self._persist_quiz(document, current_user, draft, [])
        self._refresh_progress(document, current_user, source=source)
        self.session.commit()
        loaded = self.quizzes.get_full(quiz.id, current_user.id)
        if loaded is None:
            raise NotFoundError("Generated quiz could not be loaded.")
        return loaded

    def list_quizzes(self, document_id: str, current_user: User) -> list[Quiz]:
        self._get_document(document_id)
        return list(self.quizzes.list_by_document(owner_user_id=current_user.id, document_id=document_id, limit=100))

    def start_quiz(self, quiz_id: str, current_user: User) -> StartQuizResponse:
        quiz = self.quizzes.get_full(quiz_id, current_user.id)
        if quiz is None:
            raise NotFoundError("Quiz was not found.")
        attempt = self.attempts.add(
            QuizAttempt(
                quiz_id=quiz.id,
                owner_user_id=current_user.id,
                status="started",
                started_at=utc_now(),
                submitted_at=None,
                time_spent_seconds=0,
                answers={},
                score=0.0,
                total_points=sum(question.points for question in quiz.questions),
                accuracy=0.0,
                passed=False,
                feedback=[],
                metadata_json={"source": "adaptive_learning_quiz"},
            )
        )
        self.session.commit()
        return StartQuizResponse(attempt=attempt, quiz=quiz)

    def submit_quiz(
        self,
        attempt_id: str,
        payload: SubmitQuizRequest,
        current_user: User,
    ) -> SubmitQuizResponse:
        attempt = self.attempts.get_owned(attempt_id, current_user.id)
        if attempt is None:
            raise NotFoundError("Quiz attempt was not found.")
        if attempt.status == "submitted":
            raise ConflictError("This quiz attempt has already been submitted.")

        quiz = attempt.quiz
        question_payloads = [self._question_payload(question) for question in quiz.questions]
        grading = self.quiz_engine.grade(question_payloads, payload.answers)
        now = utc_now()
        attempt.status = "submitted"
        attempt.submitted_at = now
        attempt.time_spent_seconds = payload.time_spent_seconds
        attempt.answers = payload.answers
        attempt.score = float(grading["score"])
        attempt.total_points = float(grading["total_points"])
        attempt.accuracy = float(grading["accuracy"])
        attempt.passed = bool(grading["passed"])
        attempt.feedback = list(grading["feedback"])
        attempt.metadata_json = {**attempt.metadata_json, "graded_at": now.isoformat()}
        correct_count = sum(1 for item in attempt.feedback if item.get("correct") is True)
        self.sessions.add(
            LearningSession(
                owner_user_id=current_user.id,
                document_id=quiz.document_id,
                session_type="quiz",
                title=f"{quiz.title} attempt",
                status="completed",
                started_at=attempt.started_at,
                ended_at=now,
                duration_seconds=payload.time_spent_seconds,
                items_studied=len(quiz.questions),
                correct_count=correct_count,
                total_count=len(quiz.questions),
                mastery_delta=attempt.accuracy,
                metadata_json={"quiz_id": quiz.id, "attempt_id": attempt.id},
            )
        )
        document = self._get_document(quiz.document_id)
        source = self._source_from_document(document)
        progress = self._refresh_progress(document, current_user, source=source)
        earned = self._persist_achievements(
            current_user,
            self.achievement_engine.review_achievements(
                streak_days=progress.streak_days,
                mastery_percentage=self._average_mastery(document.id, current_user.id),
                quiz_accuracy=attempt.accuracy,
            ),
        )
        certificate = self._maybe_issue_certificate(document, current_user, attempt, progress)
        self.session.commit()
        return SubmitQuizResponse(attempt=attempt, progress=progress, achievements=earned, certificate=certificate)

    def review_flashcards(
        self,
        payload: ReviewFlashcardsRequest,
        current_user: User,
    ) -> ReviewFlashcardsResponse:
        document_ids: set[str] = set()
        created_reviews: list[Review] = []
        updated_memory: list[MemoryTracking] = []
        for item in payload.reviews:
            flashcard = self.flashcards.get(item.flashcard_id)
            if flashcard is None or flashcard.owner_user_id != current_user.id:
                raise NotFoundError("Flashcard was not found.")
            document_ids.add(flashcard.document_id)
            memory = self.memory.get_by_flashcard(owner_user_id=current_user.id, flashcard_id=flashcard.id)
            if memory is None:
                memory = self._persist_memory_for_flashcard(flashcard, current_user)
            old_state = self._memory_state(memory)
            new_state = self.scheduler.schedule(old_state, item.rating, confidence=item.confidence)
            review = self.reviews.add(
                Review(
                    owner_user_id=current_user.id,
                    flashcard_id=flashcard.id,
                    rating=item.rating.value,
                    response_quality=item.response_quality,
                    correct=item.rating.value != "again",
                    confidence=item.confidence,
                    reviewed_at=new_state.last_review_at or utc_now(),
                    scheduled_before=old_state.next_review_at,
                    next_review_at=new_state.next_review_at,
                    memory_strength=new_state.memory_strength,
                    retention_score=new_state.retention_score,
                    duration_ms=item.duration_ms,
                    metadata_json={"mastery_percentage": new_state.mastery_percentage},
                )
            )
            self._apply_memory_state(memory, new_state)
            memory.metadata_json = {
                **memory.metadata_json,
                "last_rating": item.rating.value,
                "last_response_quality": item.response_quality,
            }
            created_reviews.append(review)
            updated_memory.append(memory)

        if len(document_ids) != 1:
            raise ValidationError("Review submissions must belong to one document at a time.")
        document = self._get_document(next(iter(document_ids)))
        now = utc_now()
        self.sessions.add(
            LearningSession(
                owner_user_id=current_user.id,
                document_id=document.id,
                session_type="flashcard_review",
                title=f"{document.title} flashcard review",
                status="completed",
                started_at=now,
                ended_at=now,
                duration_seconds=sum(item.duration_ms for item in payload.reviews) // 1000,
                items_studied=len(payload.reviews),
                correct_count=sum(1 for item in payload.reviews if item.rating.value != "again"),
                total_count=len(payload.reviews),
                mastery_delta=self._average_mastery(document.id, current_user.id) / 100,
                metadata_json={"review_count": len(payload.reviews)},
            )
        )
        source = self._source_from_document(document)
        progress = self._refresh_progress(document, current_user, source=source)
        earned = self._persist_achievements(
            current_user,
            self.achievement_engine.review_achievements(
                streak_days=progress.streak_days,
                mastery_percentage=self._average_mastery(document.id, current_user.id),
                quiz_accuracy=progress.quiz_accuracy,
            ),
        )
        self.session.commit()
        return ReviewFlashcardsResponse(
            reviews=created_reviews,
            memory=updated_memory,
            progress=progress,
            achievements=earned,
        )

    def progress_for_user(
        self,
        current_user: User,
        *,
        document_id: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> LearningProgressResponse:
        if document_id is not None:
            document = self._get_document(document_id)
            progress = self._get_or_create_progress(document, current_user, self._source_from_document(document))
            return LearningProgressResponse(progress=[progress])
        return LearningProgressResponse(
            progress=list(self.progress.list_owned(owner_user_id=current_user.id, offset=offset, limit=limit))
        )

    def list_achievements(self, current_user: User, *, offset: int = 0, limit: int = 100) -> list[Achievement]:
        return list(self.achievements.list_owned(owner_user_id=current_user.id, offset=offset, limit=limit))

    def list_certificates(self, current_user: User, *, offset: int = 0, limit: int = 100) -> list[Certificate]:
        return list(self.certificates.list_owned(owner_user_id=current_user.id, offset=offset, limit=limit))

    def generate_revision_plan(
        self,
        document_id: str,
        payload: GenerateRevisionPlanRequest,
        current_user: User,
    ) -> RevisionPlan:
        document = self._get_document(document_id)
        source = self._source_from_document(document)
        existing = [
            plan
            for plan in self.revision_plans.list_by_document(owner_user_id=current_user.id, document_id=document.id)
            if plan.plan_type == payload.plan_type.value
        ]
        if existing:
            return existing[0]
        draft = next(plan for plan in self.revision_engine.generate(source) if plan.plan_type == payload.plan_type)
        plan = self._persist_revision_plan(document, current_user, draft)
        self.background.schedule_revision_reviews([plan])
        self._refresh_progress(document, current_user, source=source)
        self.session.commit()
        return plan

    def list_revision_plans(self, document_id: str, current_user: User) -> list[RevisionPlan]:
        self._get_document(document_id)
        return list(self.revision_plans.list_by_document(owner_user_id=current_user.id, document_id=document_id))

    def list_coding_challenges(self, document_id: str, current_user: User) -> list[CodingChallenge]:
        self._get_document(document_id)
        return list(self.coding_challenges.list_by_document(owner_user_id=current_user.id, document_id=document_id))

    def interview_questions(self, document_id: str, current_user: User) -> list[dict[str, object]]:
        self._get_document(document_id)
        quiz = self._latest_quiz(document_id, current_user.id)
        if quiz is None:
            return []
        questions = quiz.metadata_json.get("interview_questions", [])
        return questions if isinstance(questions, list) else []

    def _persist_flashcards(
        self,
        document: Document,
        current_user: User,
        drafts: Sequence[FlashcardDraft],
    ) -> list[Flashcard]:
        flashcards: list[Flashcard] = []
        for draft in drafts:
            flashcard = self.flashcards.add(
                Flashcard(
                    owner_user_id=current_user.id,
                    document_id=document.id,
                    card_type=draft.card_type.value,
                    difficulty=draft.difficulty.value,
                    front=draft.front,
                    back=draft.back,
                    explanation=draft.explanation,
                    tags=draft.tags,
                    source_excerpt=draft.source_excerpt,
                    active=True,
                    metadata_json=draft.metadata,
                )
            )
            self._persist_memory_for_flashcard(flashcard, current_user)
            flashcards.append(flashcard)
        return flashcards

    def _persist_memory_for_flashcard(self, flashcard: Flashcard, current_user: User) -> MemoryTracking:
        state = self.scheduler.initial_state()
        concept = (
            str(flashcard.metadata_json.get("concept") or flashcard.metadata_json.get("term") or "")
            or (flashcard.tags[-1] if flashcard.tags else flashcard.front[:80])
        )
        return self.memory.add(
            MemoryTracking(
                owner_user_id=current_user.id,
                document_id=flashcard.document_id,
                flashcard_id=flashcard.id,
                concept=concept[:220],
                memory_strength=state.memory_strength,
                confidence=state.confidence,
                retention_score=state.retention_score,
                review_count=state.review_count,
                success_rate=state.success_rate,
                last_review_at=state.last_review_at,
                next_review_at=state.next_review_at,
                forgetting_curve=state.forgetting_curve,
                mastery_percentage=state.mastery_percentage,
                metadata_json={"scheduler": "fsrs_inspired_v1"},
            )
        )

    def _persist_quiz(
        self,
        document: Document,
        current_user: User,
        draft: QuizDraft,
        interview_questions: Sequence[InterviewQuestionDraft],
    ) -> Quiz:
        quiz = self.quizzes.add(
            Quiz(
                owner_user_id=current_user.id,
                document_id=document.id,
                title=draft.title,
                quiz_type=draft.quiz_type,
                difficulty=draft.difficulty.value,
                time_limit_seconds=draft.time_limit_seconds,
                adaptive=draft.adaptive,
                status="active",
                metadata_json={
                    **draft.metadata,
                    "interview_questions": [self._interview_payload(item) for item in interview_questions],
                    "knowledge_test": True,
                },
            )
        )
        for index, question in enumerate(draft.questions, start=1):
            quiz.questions.append(
                QuizQuestion(
                    order_index=index,
                    question_type=question.question_type.value,
                    prompt=question.prompt,
                    choices=question.choices,
                    correct_answers=question.correct_answers,
                    explanation=question.explanation,
                    difficulty=question.difficulty.value,
                    points=question.points,
                    metadata_json=question.metadata,
                )
            )
        self.session.flush()
        return quiz

    def _persist_coding_challenges(
        self,
        document: Document,
        current_user: User,
        drafts: Sequence[CodingChallengeDraft],
    ) -> list[CodingChallenge]:
        return [
            self.coding_challenges.add(
                CodingChallenge(
                    owner_user_id=current_user.id,
                    document_id=document.id,
                    title=draft.title,
                    difficulty=draft.difficulty.value,
                    prompt=draft.prompt,
                    starter_code=draft.starter_code,
                    hints=draft.hints,
                    optimal_solution=draft.optimal_solution,
                    complexity_analysis=draft.complexity_analysis,
                    alternative_solutions=draft.alternative_solutions,
                    edge_cases=draft.edge_cases,
                    unit_tests=draft.unit_tests,
                    tags=draft.tags,
                    status="active",
                    metadata_json=draft.metadata,
                )
            )
            for draft in drafts
        ]

    def _persist_revision_plans(
        self,
        document: Document,
        current_user: User,
        drafts: Sequence[RevisionPlanDraft],
    ) -> list[RevisionPlan]:
        plans = [self._persist_revision_plan(document, current_user, draft) for draft in drafts]
        self.background.schedule_revision_reviews(plans)
        return plans

    def _persist_revision_plan(
        self,
        document: Document,
        current_user: User,
        draft: RevisionPlanDraft,
    ) -> RevisionPlan:
        return self.revision_plans.add(
            RevisionPlan(
                owner_user_id=current_user.id,
                document_id=document.id,
                plan_type=draft.plan_type.value,
                title=draft.title,
                schedule=draft.schedule,
                focus_concepts=draft.focus_concepts,
                estimated_minutes=draft.estimated_minutes,
                status="active",
                due_at=None,
                metadata_json=draft.metadata,
            )
        )

    def _persist_progress(
        self,
        document: Document,
        current_user: User,
        bundle: AdaptiveLearningBundle,
        flashcards: Sequence[Flashcard],
        quiz: Quiz,
        coding_challenges: Sequence[CodingChallenge],
    ) -> Progress:
        total_items = len(flashcards) + len(quiz.questions) + len(coding_challenges)
        progress = self.progress.get_by_document(owner_user_id=current_user.id, document_id=document.id)
        if progress is None:
            progress = self.progress.add(
                Progress(
                    owner_user_id=current_user.id,
                    document_id=document.id,
                    knowledge_score=bundle.analytics.knowledge_score,
                    retention_score=bundle.analytics.retention_score,
                    weak_concepts=bundle.analytics.weak_concepts,
                    strong_concepts=bundle.analytics.strong_concepts,
                    learning_velocity=bundle.analytics.learning_velocity,
                    quiz_accuracy=bundle.analytics.quiz_accuracy,
                    memory_heatmap=bundle.analytics.memory_heatmap,
                    study_time_minutes=bundle.analytics.study_time_minutes,
                    completion_rate=bundle.analytics.completion_rate,
                    mastery_graph=bundle.analytics.mastery_graph,
                    mastered_items=0,
                    total_items=total_items,
                    streak_days=0,
                    last_activity_at=None,
                    metadata_json={
                        "document_title": document.title,
                        "learning_path": self._learning_path_payload(bundle),
                        "knowledge_tests": [quiz.id],
                    },
                )
            )
            return progress
        progress.total_items = total_items
        progress.metadata_json = {
            **progress.metadata_json,
            "learning_path": self._learning_path_payload(bundle),
            "knowledge_tests": [quiz.id],
        }
        return progress

    def _persist_achievements(
        self,
        current_user: User,
        drafts: Sequence[AchievementDraft],
    ) -> list[Achievement]:
        created: list[Achievement] = []
        for draft in drafts:
            if self.achievements.exists(
                owner_user_id=current_user.id,
                achievement_type=draft.achievement_type,
                title=draft.title,
            ):
                continue
            achievement = self.achievements.add(
                Achievement(
                    owner_user_id=current_user.id,
                    achievement_type=draft.achievement_type,
                    title=draft.title,
                    description=draft.description,
                    badge=draft.badge,
                    skill_level=draft.skill_level,
                    points=draft.points,
                    awarded_at=utc_now(),
                    metadata_json=draft.metadata,
                )
            )
            created.append(achievement)
        return created

    def _maybe_issue_certificate(
        self,
        document: Document,
        current_user: User,
        attempt: QuizAttempt,
        progress: Progress,
    ) -> Certificate | None:
        if attempt.accuracy < 0.9:
            return None
        existing_statement = (
            select(Certificate)
            .where(Certificate.owner_user_id == current_user.id)
            .where(Certificate.document_id == document.id)
            .where(Certificate.certificate_type == "knowledge_test_completion")
        )
        existing = self.session.scalars(existing_statement).first()
        if existing is not None:
            return existing
        verification = f"RF-{stable_hash(f'{current_user.id}:{document.id}:{attempt.id}')[:14].upper()}"
        return self.certificates.add(
            Certificate(
                owner_user_id=current_user.id,
                document_id=document.id,
                title=f"{document.title} Knowledge Mastery",
                certificate_type="knowledge_test_completion",
                issued_at=utc_now(),
                score=attempt.accuracy,
                mastery_percentage=max(progress.knowledge_score * 100, attempt.accuracy * 100),
                verification_code=verification,
                metadata_json={"quiz_attempt_id": attempt.id, "document_title": document.title},
            )
        )

    def _refresh_progress(
        self,
        document: Document,
        current_user: User,
        *,
        source: LearningSource | None = None,
        progress: Progress | None = None,
    ) -> Progress:
        source = source or self._source_from_document(document)
        progress = progress or self._get_or_create_progress(document, current_user, source)
        previous_activity = progress.last_activity_at
        memory_records = list(self.memory.list_by_document(owner_user_id=current_user.id, document_id=document.id))
        sessions = self._document_sessions(document.id, current_user.id)
        revision_plans = list(
            self.revision_plans.list_by_document(owner_user_id=current_user.id, document_id=document.id, limit=100)
        )
        total_items = self._total_learning_items(document.id, current_user.id)
        result = self.background.run_document_maintenance(
            source=source,
            progress=progress,
            memory_records=memory_records,
            revision_plans=revision_plans,
            sessions=sessions,
            quiz_accuracy=self._latest_quiz_accuracy(document.id, current_user.id),
            total_items=total_items,
        )
        reminders = self.background.schedule_reminders(memory_records)
        result.progress.streak_days = self._next_streak(previous_activity, result.progress.streak_days)
        result.progress.metadata_json = {
            **result.progress.metadata_json,
            "due_review_count": result.due_review_count,
            "overdue_review_count": result.overdue_review_count,
            "active_revision_count": result.active_revision_count,
            "reminders": reminders,
        }
        return result.progress

    def _get_or_create_progress(self, document: Document, current_user: User, source: LearningSource) -> Progress:
        progress = self.progress.get_by_document(owner_user_id=current_user.id, document_id=document.id)
        if progress is not None:
            return progress
        analytics = self.engine.analytics.summarize(source)
        return self.progress.add(
            Progress(
                owner_user_id=current_user.id,
                document_id=document.id,
                knowledge_score=analytics.knowledge_score,
                retention_score=analytics.retention_score,
                weak_concepts=analytics.weak_concepts,
                strong_concepts=analytics.strong_concepts,
                learning_velocity=analytics.learning_velocity,
                quiz_accuracy=analytics.quiz_accuracy,
                memory_heatmap=analytics.memory_heatmap,
                study_time_minutes=analytics.study_time_minutes,
                completion_rate=analytics.completion_rate,
                mastery_graph=analytics.mastery_graph,
                mastered_items=0,
                total_items=self._total_learning_items(document.id, current_user.id),
                streak_days=0,
                last_activity_at=None,
                metadata_json={"document_title": document.title},
            )
        )

    def _bundle_response(
        self,
        document_id: str,
        current_user: User,
        *,
        progress: Progress | None = None,
        achievements: Sequence[Achievement] | None = None,
    ) -> LearningBundleRead:
        flashcards = list(
            self.flashcards.list_by_document(
                owner_user_id=current_user.id,
                document_id=document_id,
                limit=500,
            )
        )
        quiz = self._latest_quiz(document_id, current_user.id)
        if quiz is None:
            raise NotFoundError("Adaptive learning quiz was not found.")
        coding_challenges = list(
            self.coding_challenges.list_by_document(owner_user_id=current_user.id, document_id=document_id, limit=100)
        )
        revision_plans = list(
            self.revision_plans.list_by_document(owner_user_id=current_user.id, document_id=document_id, limit=100)
        )
        document = self._get_document(document_id)
        progress = progress or self._get_or_create_progress(
            document,
            current_user,
            self._source_from_document(document),
        )
        return LearningBundleRead(
            document_id=document_id,
            flashcards=flashcards,
            quiz=quiz,
            interview_questions=self.interview_questions(document_id, current_user),
            coding_challenges=coding_challenges,
            revision_plans=revision_plans,
            progress=progress,
            achievements=list(achievements or self.achievements.list_owned(owner_user_id=current_user.id)),
        )

    def _delete_document_learning(self, document_id: str, owner_user_id: str) -> None:
        for attempt in self._quiz_attempts_for_document(document_id, owner_user_id):
            self.session.delete(attempt)
        for quiz in self.quizzes.list_by_document(owner_user_id=owner_user_id, document_id=document_id, limit=1000):
            self.session.delete(quiz)
        for flashcard in self.flashcards.list_by_document(
            owner_user_id=owner_user_id,
            document_id=document_id,
            limit=1000,
        ):
            self.session.delete(flashcard)
        for challenge in self.coding_challenges.list_by_document(
            owner_user_id=owner_user_id,
            document_id=document_id,
            limit=1000,
        ):
            self.session.delete(challenge)
        for plan in self.revision_plans.list_by_document(
            owner_user_id=owner_user_id,
            document_id=document_id,
            limit=1000,
        ):
            self.session.delete(plan)
        progress = self.progress.get_by_document(owner_user_id=owner_user_id, document_id=document_id)
        if progress is not None:
            self.session.delete(progress)
        for session in self._document_sessions(document_id, owner_user_id):
            self.session.delete(session)
        self.session.flush()

    def _source_from_document(self, document: Document) -> LearningSource:
        keywords = [keyword.value for keyword in document.keywords] or document.topics
        technologies = [technology.name for technology in document.technologies]
        summaries = {summary.summary_type: summary.content for summary in document.summaries}
        concepts = [
            LearningConcept(
                name=concept.name,
                description=concept.description,
                difficulty=self._card_difficulty(concept.difficulty_level),
                keywords=keywords[:8],
                source_excerpt=excerpt_for(concept.name, document.cleaned_text, fallback=concept.description),
            )
            for concept in document.concepts
        ]
        if not concepts:
            concepts = [
                LearningConcept(
                    name=topic,
                    description=f"{topic} is a key topic in {document.title}.",
                    difficulty=self._card_difficulty(document.difficulty),
                    keywords=keywords[:8],
                    source_excerpt=excerpt_for(topic, document.cleaned_text, fallback=document.cleaned_text[:320]),
                )
                for topic in (document.topics or keywords[:8] or [document.title])
            ]
        return LearningSource(
            document_id=document.id,
            title=document.title,
            category=document.category,
            difficulty=document.difficulty,
            topics=document.topics,
            concepts=concepts,
            keywords=keywords,
            technologies=technologies,
            definitions=document.definitions or [],
            algorithms=document.algorithms or [],
            equations=document.equations or [],
            code_snippets=document.code_snippets or [],
            summaries=summaries,
            learning_objectives=document.learning_objectives or [],
            cleaned_text=document.cleaned_text,
        )

    def _get_document(self, document_id: str) -> Document:
        document = self.documents.get_full(document_id)
        if document is None:
            raise NotFoundError("Document was not found.")
        return document

    def _card_difficulty(self, value: str) -> CardDifficulty:
        normalized = value.casefold()
        if normalized in {"beginner", "easy"}:
            return CardDifficulty.EASY
        if normalized in {"advanced", "hard"}:
            return CardDifficulty.HARD
        if normalized in {"expert"}:
            return CardDifficulty.EXPERT
        return CardDifficulty.MEDIUM

    def _latest_quiz(self, document_id: str, owner_user_id: str) -> Quiz | None:
        quizzes = list(self.quizzes.list_by_document(owner_user_id=owner_user_id, document_id=document_id, limit=1))
        return quizzes[0] if quizzes else None

    def _latest_quiz_accuracy(self, document_id: str, owner_user_id: str) -> float:
        statement = (
            select(QuizAttempt)
            .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
            .where(Quiz.document_id == document_id)
            .where(QuizAttempt.owner_user_id == owner_user_id)
            .where(QuizAttempt.status == "submitted")
            .order_by(QuizAttempt.submitted_at.desc())
        )
        attempt = self.session.scalars(statement).first()
        return float(attempt.accuracy) if attempt is not None else 0.0

    def _quiz_attempts_for_document(self, document_id: str, owner_user_id: str) -> list[QuizAttempt]:
        statement = (
            select(QuizAttempt)
            .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
            .where(Quiz.document_id == document_id)
            .where(QuizAttempt.owner_user_id == owner_user_id)
        )
        return list(self.session.scalars(statement).all())

    def _document_sessions(self, document_id: str, owner_user_id: str) -> list[LearningSession]:
        statement = (
            select(LearningSession)
            .where(LearningSession.document_id == document_id)
            .where(LearningSession.owner_user_id == owner_user_id)
        )
        return list(self.session.scalars(statement).all())

    def _total_learning_items(self, document_id: str, owner_user_id: str) -> int:
        flashcard_count = len(
            self.flashcards.list_by_document(owner_user_id=owner_user_id, document_id=document_id, limit=1000)
        )
        quiz = self._latest_quiz(document_id, owner_user_id)
        question_count = len(quiz.questions) if quiz is not None else 0
        challenge_count = len(
            self.coding_challenges.list_by_document(owner_user_id=owner_user_id, document_id=document_id, limit=1000)
        )
        return flashcard_count + question_count + challenge_count

    def _average_mastery(self, document_id: str, owner_user_id: str) -> float:
        records = self.memory.list_by_document(owner_user_id=owner_user_id, document_id=document_id)
        if not records:
            return 0.0
        return round(sum(record.mastery_percentage for record in records) / len(records), 2)

    def _question_payload(self, question: QuizQuestion) -> dict[str, object]:
        return {
            "id": question.id,
            "points": question.points,
            "correct_answers": question.correct_answers,
            "explanation": question.explanation,
        }

    def _memory_state(self, memory: MemoryTracking) -> MemoryState:
        return MemoryState(
            memory_strength=memory.memory_strength,
            confidence=memory.confidence,
            retention_score=memory.retention_score,
            review_count=memory.review_count,
            success_rate=memory.success_rate,
            last_review_at=memory.last_review_at,
            next_review_at=memory.next_review_at,
            forgetting_curve=memory.forgetting_curve,
            mastery_percentage=memory.mastery_percentage,
        )

    def _apply_memory_state(self, memory: MemoryTracking, state: MemoryState) -> None:
        memory.memory_strength = state.memory_strength
        memory.confidence = state.confidence
        memory.retention_score = state.retention_score
        memory.review_count = state.review_count
        memory.success_rate = state.success_rate
        memory.last_review_at = state.last_review_at
        memory.next_review_at = state.next_review_at
        memory.forgetting_curve = state.forgetting_curve
        memory.mastery_percentage = state.mastery_percentage

    def _interview_payload(self, question: InterviewQuestionDraft) -> dict[str, object]:
        return {
            "question_type": question.question_type.value,
            "difficulty": question.difficulty.value,
            "question": question.question,
            "ideal_answer": question.ideal_answer,
            "follow_ups": question.follow_ups,
            "evaluation_points": question.evaluation_points,
            "metadata": question.metadata,
        }

    def _learning_path_payload(self, bundle: AdaptiveLearningBundle) -> list[dict[str, Any]]:
        return [
            {
                "order": 1,
                "activity": "Review generated flashcards",
                "item_count": len(bundle.flashcards),
            },
            {
                "order": 2,
                "activity": "Complete adaptive knowledge test",
                "item_count": len(bundle.quiz.questions),
            },
            {
                "order": 3,
                "activity": "Practice interview explanations",
                "item_count": len(bundle.interview_questions),
            },
            {
                "order": 4,
                "activity": "Solve coding challenges",
                "item_count": len(bundle.coding_challenges),
            },
            {
                "order": 5,
                "activity": "Follow revision plans",
                "item_count": len(bundle.revision_plans),
            },
        ]

    def _next_streak(self, previous_activity: object, current_streak: int) -> int:
        if previous_activity is None:
            return max(1, current_streak)
        if not hasattr(previous_activity, "date"):
            return max(1, current_streak)
        today = utc_now().date()
        previous_date = previous_activity.date()
        if previous_date == today:
            return max(1, current_streak)
        if previous_date == today - timedelta(days=1):
            return current_streak + 1
        return 1
