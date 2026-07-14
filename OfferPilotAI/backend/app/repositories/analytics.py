"""Analytics repositories."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnswerEvaluation, Interview, Question


class AnalyticsRepository:
    """Read-only analytics persistence adapter."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_evaluation_rows(self, *, user_id: str) -> Sequence[tuple[AnswerEvaluation, str, Interview]]:
        result = await self.session.execute(
            select(AnswerEvaluation, Question.category, Interview)
            .join(Question, Question.id == AnswerEvaluation.question_id)
            .join(Interview, Interview.id == AnswerEvaluation.interview_id)
            .where(AnswerEvaluation.user_id == user_id)
            .order_by(AnswerEvaluation.created_at.asc())
        )
        return result.all()

    async def list_interviews(self, *, user_id: str, limit: int = 20) -> Sequence[Interview]:
        result = await self.session.execute(
            select(Interview)
            .where(Interview.user_id == user_id)
            .order_by(Interview.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
