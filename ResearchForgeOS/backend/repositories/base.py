from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from backend.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def get(self, entity_id: str) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def list(self, *, offset: int = 0, limit: int = 50) -> Sequence[ModelT]:
        statement = select(self.model).offset(offset).limit(limit)
        return self.session.scalars(statement).all()

    def count(self, statement: Select[tuple[ModelT]] | None = None) -> int:
        if statement is None:
            return self.session.scalar(select(func.count()).select_from(self.model)) or 0
        count_statement = select(func.count()).select_from(statement.subquery())
        return self.session.scalar(count_statement) or 0

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()
