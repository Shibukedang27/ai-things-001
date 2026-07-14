"""Generic CRUD service layer."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.db.base import Base
from app.repositories.base import SQLAlchemyRepository

ModelT = TypeVar("ModelT", bound=Base)
RepositoryT = TypeVar("RepositoryT", bound=SQLAlchemyRepository)


class CRUDService(Generic[ModelT, RepositoryT]):
    """Transactional CRUD service backed by a repository."""

    repository_cls: type[RepositoryT]
    resource_name = "resource"

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = self.repository_cls(session)

    def prepare_create_values(self, values: dict[str, Any]) -> dict[str, Any]:
        """Normalize create values before persistence."""

        return values

    def prepare_update_values(self, values: dict[str, Any]) -> dict[str, Any]:
        """Normalize update values before persistence."""

        return values

    async def list(self, *, page: int = 1, page_size: int = 25) -> tuple[list[ModelT], int]:
        offset = (page - 1) * page_size
        total = await self.repository.count()
        items = list(await self.repository.list(offset=offset, limit=page_size))
        return items, total

    async def get(self, entity_id: str) -> ModelT:
        entity = await self.repository.get(entity_id)
        if entity is None:
            raise NotFoundError(f"{self.resource_name.title()} not found.")
        return entity

    async def create(self, payload: BaseModel) -> ModelT:
        values = self.prepare_create_values(payload.model_dump(exclude_unset=True))
        try:
            entity = await self.repository.create(values)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError(f"{self.resource_name.title()} violates a database constraint.") from exc

    async def update(self, entity_id: str, payload: BaseModel) -> ModelT:
        entity = await self.get(entity_id)
        values: dict[str, Any] = self.prepare_update_values(payload.model_dump(exclude_unset=True))
        try:
            updated_entity = await self.repository.update(entity, values)
            await self.session.commit()
            await self.session.refresh(updated_entity)
            return updated_entity
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError(f"{self.resource_name.title()} violates a database constraint.") from exc

    async def delete(self, entity_id: str) -> None:
        entity = await self.get(entity_id)
        try:
            await self.repository.delete(entity)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError(f"{self.resource_name.title()} cannot be deleted because it is still referenced.") from exc
