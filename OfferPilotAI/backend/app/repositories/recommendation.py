"""Learning recommendation repository."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnswerEvaluation, Interview, InterviewHistory, LearningRoadmap, Question


class LearningRecommendationRepository:
    """Persistence adapter for learning recommendation workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_evaluation_context(
        self,
        *,
        user_id: str,
        interview_id: str | None = None,
    ) -> Sequence[tuple[AnswerEvaluation, Question, Interview]]:
        statement = (
            select(AnswerEvaluation, Question, Interview)
            .join(Question, Question.id == AnswerEvaluation.question_id)
            .join(Interview, Interview.id == AnswerEvaluation.interview_id)
            .where(AnswerEvaluation.user_id == user_id)
            .order_by(AnswerEvaluation.created_at.desc())
        )
        if interview_id:
            statement = statement.where(AnswerEvaluation.interview_id == interview_id)

        result = await self.session.execute(statement)
        return result.all()

    async def list_history(
        self,
        *,
        user_id: str,
        interview_id: str | None = None,
    ) -> Sequence[InterviewHistory]:
        statement = select(InterviewHistory).where(InterviewHistory.user_id == user_id).order_by(
            InterviewHistory.occurred_at.desc()
        )
        if interview_id:
            statement = statement.where(InterviewHistory.interview_id == interview_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create_roadmap(self, values: dict) -> LearningRoadmap:
        roadmap = LearningRoadmap(**values)
        self.session.add(roadmap)
        await self.session.flush()
        return roadmap

    async def latest_roadmap(self, *, user_id: str) -> LearningRoadmap | None:
        result = await self.session.execute(
            select(LearningRoadmap)
            .where(LearningRoadmap.user_id == user_id)
            .order_by(LearningRoadmap.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
