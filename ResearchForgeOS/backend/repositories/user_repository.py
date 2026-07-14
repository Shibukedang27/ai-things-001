from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.models.role import Role
from backend.models.user import User
from backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        statement = (
            select(User)
            .where(User.email == email.lower())
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return self.session.scalars(statement).first()

    def get_with_roles(self, user_id: str) -> User | None:
        statement = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return self.session.scalars(statement).first()

    def list_with_roles(self, *, offset: int = 0, limit: int = 50) -> Sequence[User]:
        statement = (
            select(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def total_users(self) -> int:
        return self.session.scalar(select(func.count()).select_from(User)) or 0
