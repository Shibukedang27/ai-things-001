"""Evaluation repository."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, AnswerEvaluation, Interview, Question
from app.repositories.base import SQLAlchemyRepository


class AnswerEvaluationRepository(SQLAlchemyRepository[AnswerEvaluation]):
    """Persistence adapter for answer evaluations."""

    model = AnswerEvaluation

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_answer_for_user(self, *, answer_id: str, user_id: str) -> Answer | None:
        result = await self.session.execute(
            select(Answer).where(Answer.id == answer_id, Answer.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_interview_for_user(self, *, interview_id: str, user_id: str) -> Interview | None:
        result = await self.session.execute(
            select(Interview).where(Interview.id == interview_id, Interview.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_question(self, question_id: str) -> Question | None:
        return await self.session.get(Question, question_id)

    async def get_existing_for_answer(self, answer_id: str) -> AnswerEvaluation | None:
        result = await self.session.execute(
            select(AnswerEvaluation).where(AnswerEvaluation.answer_id == answer_id)
        )
        return result.scalar_one_or_none()

    async def list_answers_for_interview(self, *, interview_id: str, user_id: str) -> Sequence[Answer]:
        result = await self.session.execute(
            select(Answer)
            .where(Answer.interview_id == interview_id, Answer.user_id == user_id)
            .order_by(Answer.created_at.asc())
        )
        return result.scalars().all()

    async def list_for_interview(self, *, interview_id: str, user_id: str) -> Sequence[AnswerEvaluation]:
        result = await self.session.execute(
            select(AnswerEvaluation)
            .where(AnswerEvaluation.interview_id == interview_id, AnswerEvaluation.user_id == user_id)
            .order_by(AnswerEvaluation.created_at.asc())
        )
        return result.scalars().all()
