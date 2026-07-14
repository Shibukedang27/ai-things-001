"""Session repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session
from app.repositories.base import SQLAlchemyRepository


class SessionRepository(SQLAlchemyRepository[Session]):
    model = Session

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_token_jti(self, token_jti: str) -> Session | None:
        result = await self.session.execute(select(Session).where(Session.token_jti == token_jti))
        return result.scalar_one_or_none()
