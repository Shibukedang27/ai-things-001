from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

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
from backend.repositories.base import BaseRepository


class FlashcardRepository(BaseRepository[Flashcard]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Flashcard)

    def list_by_document(self, *, owner_user_id: str, document_id: str, limit: int = 200) -> Sequence[Flashcard]:
        statement = (
            select(Flashcard)
            .where(Flashcard.owner_user_id == owner_user_id)
            .where(Flashcard.document_id == document_id)
            .order_by(Flashcard.difficulty.asc(), Flashcard.card_type.asc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def due_cards(self, *, owner_user_id: str, limit: int = 100) -> Sequence[Flashcard]:
        statement = (
            select(Flashcard)
            .join(MemoryTracking, MemoryTracking.flashcard_id == Flashcard.id)
            .where(Flashcard.owner_user_id == owner_user_id)
            .where(Flashcard.active.is_(True))
            .order_by(MemoryTracking.next_review_at.asc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Quiz)

    def get_full(self, quiz_id: str, owner_user_id: str) -> Quiz | None:
        statement = (
            select(Quiz)
            .where(Quiz.id == quiz_id)
            .where(Quiz.owner_user_id == owner_user_id)
            .options(selectinload(Quiz.questions), selectinload(Quiz.attempts))
        )
        return self.session.scalars(statement).first()

    def list_by_document(self, *, owner_user_id: str, document_id: str, limit: int = 50) -> Sequence[Quiz]:
        statement = (
            select(Quiz)
            .where(Quiz.owner_user_id == owner_user_id)
            .where(Quiz.document_id == document_id)
            .options(selectinload(Quiz.questions))
            .order_by(Quiz.created_at.desc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()


class QuizQuestionRepository(BaseRepository[QuizQuestion]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, QuizQuestion)


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, QuizAttempt)

    def get_owned(self, attempt_id: str, owner_user_id: str) -> QuizAttempt | None:
        statement = (
            select(QuizAttempt)
            .where(QuizAttempt.id == attempt_id)
            .where(QuizAttempt.owner_user_id == owner_user_id)
            .options(selectinload(QuizAttempt.quiz).selectinload(Quiz.questions))
        )
        return self.session.scalars(statement).first()


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Review)


class LearningSessionRepository(BaseRepository[LearningSession]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, LearningSession)


class AchievementRepository(BaseRepository[Achievement]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Achievement)

    def list_owned(self, *, owner_user_id: str, offset: int = 0, limit: int = 100) -> Sequence[Achievement]:
        statement = (
            select(Achievement)
            .where(Achievement.owner_user_id == owner_user_id)
            .order_by(Achievement.awarded_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def exists(self, *, owner_user_id: str, achievement_type: str, title: str) -> bool:
        statement = (
            select(Achievement.id)
            .where(Achievement.owner_user_id == owner_user_id)
            .where(Achievement.achievement_type == achievement_type)
            .where(Achievement.title == title)
        )
        return self.session.scalar(statement) is not None


class CertificateRepository(BaseRepository[Certificate]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Certificate)

    def list_owned(self, *, owner_user_id: str, offset: int = 0, limit: int = 100) -> Sequence[Certificate]:
        statement = (
            select(Certificate)
            .where(Certificate.owner_user_id == owner_user_id)
            .order_by(Certificate.issued_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()


class MemoryTrackingRepository(BaseRepository[MemoryTracking]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, MemoryTracking)

    def get_by_flashcard(self, *, owner_user_id: str, flashcard_id: str) -> MemoryTracking | None:
        statement = (
            select(MemoryTracking)
            .where(MemoryTracking.owner_user_id == owner_user_id)
            .where(MemoryTracking.flashcard_id == flashcard_id)
        )
        return self.session.scalars(statement).first()

    def list_by_document(self, *, owner_user_id: str, document_id: str) -> Sequence[MemoryTracking]:
        statement = (
            select(MemoryTracking)
            .where(MemoryTracking.owner_user_id == owner_user_id)
            .where(MemoryTracking.document_id == document_id)
        )
        return self.session.scalars(statement).all()


class ProgressRepository(BaseRepository[Progress]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Progress)

    def get_by_document(self, *, owner_user_id: str, document_id: str | None) -> Progress | None:
        statement = select(Progress).where(Progress.owner_user_id == owner_user_id)
        if document_id is None:
            statement = statement.where(Progress.document_id.is_(None))
        else:
            statement = statement.where(Progress.document_id == document_id)
        return self.session.scalars(statement).first()

    def list_owned(self, *, owner_user_id: str, offset: int = 0, limit: int = 100) -> Sequence[Progress]:
        statement = (
            select(Progress)
            .where(Progress.owner_user_id == owner_user_id)
            .order_by(Progress.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()


class CodingChallengeRepository(BaseRepository[CodingChallenge]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, CodingChallenge)

    def list_by_document(self, *, owner_user_id: str, document_id: str, limit: int = 50) -> Sequence[CodingChallenge]:
        statement = (
            select(CodingChallenge)
            .where(CodingChallenge.owner_user_id == owner_user_id)
            .where(CodingChallenge.document_id == document_id)
            .order_by(CodingChallenge.difficulty.asc(), CodingChallenge.title.asc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()


class RevisionPlanRepository(BaseRepository[RevisionPlan]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RevisionPlan)

    def list_by_document(self, *, owner_user_id: str, document_id: str, limit: int = 50) -> Sequence[RevisionPlan]:
        statement = (
            select(RevisionPlan)
            .where(RevisionPlan.owner_user_id == owner_user_id)
            .where(RevisionPlan.document_id == document_id)
            .order_by(RevisionPlan.plan_type.asc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()
