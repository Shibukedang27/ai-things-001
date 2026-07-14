from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.permission import Permission
from backend.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Permission)

    def get_by_name(self, name: str) -> Permission | None:
        statement = select(Permission).where(Permission.name == name)
        return self.session.scalars(statement).first()

    def get_many_by_names(self, names: Sequence[str]) -> list[Permission]:
        if not names:
            return []
        statement = select(Permission).where(Permission.name.in_(names)).order_by(Permission.name.asc())
        return list(self.session.scalars(statement).all())

    def list_all(self) -> Sequence[Permission]:
        statement = select(Permission).order_by(Permission.resource.asc(), Permission.action.asc())
        return self.session.scalars(statement).all()
