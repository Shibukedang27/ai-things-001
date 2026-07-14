"""Resume analyzer repositories."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ResumeAnalysis
from app.repositories.base import SQLAlchemyRepository


class ResumeAnalysisRepository(SQLAlchemyRepository[ResumeAnalysis]):
    """Persistence adapter for resume analyses."""

    model = ResumeAnalysis

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_for_user(self, *, analysis_id: str, user_id: str) -> ResumeAnalysis | None:
        result = await self.session.execute(
            select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id, ResumeAnalysis.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, *, user_id: str, offset: int = 0, limit: int = 25) -> Sequence[ResumeAnalysis]:
        result = await self.session.execute(
            select(ResumeAnalysis)
            .where(ResumeAnalysis.user_id == user_id)
            .order_by(ResumeAnalysis.analyzed_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()
