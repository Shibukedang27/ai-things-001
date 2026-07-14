"""Repository operations for the interview engine."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Answer, Interview, InterviewHistory, Question


class InterviewEngineRepository:
    """Persistence adapter for interview engine workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_interview(self, values: dict) -> Interview:
        interview = Interview(**values)
        self.session.add(interview)
        await self.session.flush()
        return interview

    async def get_interview_for_user(self, *, interview_id: str, user_id: str) -> Interview | None:
        result = await self.session.execute(
            select(Interview).where(Interview.id == interview_id, Interview.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_questions(self, values: list[dict]) -> list[Question]:
        questions = [Question(**item) for item in values]
        self.session.add_all(questions)
        await self.session.flush()
        return questions

    async def list_questions(self, interview_id: str) -> Sequence[Question]:
        result = await self.session.execute(
            select(Question).where(Question.interview_id == interview_id).order_by(Question.order_index.asc())
        )
        return result.scalars().all()

    async def get_question_for_interview(self, *, interview_id: str, question_id: str) -> Question | None:
        result = await self.session.execute(
            select(Question).where(Question.id == question_id, Question.interview_id == interview_id)
        )
        return result.scalar_one_or_none()

    async def create_answer(self, values: dict) -> Answer:
        answer = Answer(**values)
        self.session.add(answer)
        await self.session.flush()
        return answer

    async def list_answers(self, *, interview_id: str, user_id: str) -> Sequence[Answer]:
        result = await self.session.execute(
            select(Answer)
            .where(Answer.interview_id == interview_id, Answer.user_id == user_id)
            .order_by(Answer.created_at.asc())
        )
        return result.scalars().all()

    async def get_answer_for_question(self, *, interview_id: str, user_id: str, question_id: str) -> Answer | None:
        result = await self.session.execute(
            select(Answer).where(
                Answer.interview_id == interview_id,
                Answer.user_id == user_id,
                Answer.question_id == question_id,
            )
        )
        return result.scalars().first()

    async def create_history(self, values: dict) -> InterviewHistory:
        history = InterviewHistory(**values)
        self.session.add(history)
        await self.session.flush()
        return history
