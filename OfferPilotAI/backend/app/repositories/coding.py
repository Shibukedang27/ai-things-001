"""Live coding repositories."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CodeSubmission, Interview
from app.repositories.base import SQLAlchemyRepository


class CodeSubmissionRepository(SQLAlchemyRepository[CodeSubmission]):
    """Persistence adapter for live-coding submissions."""

    model = CodeSubmission

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_for_user(self, *, submission_id: str, user_id: str) -> CodeSubmission | None:
        result = await self.session.execute(
            select(CodeSubmission).where(CodeSubmission.id == submission_id, CodeSubmission.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        *,
        user_id: str,
        language: str | None = None,
        offset: int = 0,
        limit: int = 25,
    ) -> Sequence[CodeSubmission]:
        statement = (
            select(CodeSubmission)
            .where(CodeSubmission.user_id == user_id)
            .order_by(CodeSubmission.submitted_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if language:
            statement = statement.where(CodeSubmission.language == language)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_interview_for_user(self, *, interview_id: str, user_id: str) -> Interview | None:
        result = await self.session.execute(
            select(Interview).where(Interview.id == interview_id, Interview.user_id == user_id)
        )
        return result.scalar_one_or_none()
