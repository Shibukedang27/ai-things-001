from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.role import Role
from backend.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Role)

    def get_by_name(self, name: str) -> Role | None:
        statement = select(Role).where(Role.name == name).options(selectinload(Role.permissions))
        return self.session.scalars(statement).first()

    def get_with_permissions(self, role_id: str) -> Role | None:
        statement = select(Role).where(Role.id == role_id).options(selectinload(Role.permissions))
        return self.session.scalars(statement).first()

    def list_with_permissions(self, *, offset: int = 0, limit: int = 50) -> Sequence[Role]:
        statement = (
            select(Role)
            .options(selectinload(Role.permissions))
            .order_by(Role.name.asc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()
