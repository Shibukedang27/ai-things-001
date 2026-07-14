"""CRUD service tests."""

import pytest
from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.services.crud import CRUDService

pytestmark = pytest.mark.asyncio


class FakeEntity:
    def __init__(self, entity_id: str, **values):
        self.id = entity_id
        for key, value in values.items():
            setattr(self, key, value)


class FakePayload(BaseModel):
    name: str


class FakeSession:
    def __init__(self):
        self.committed = False
        self.rolled_back = False
        self.refreshed = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True

    async def refresh(self, entity):
        self.refreshed = True


class FakeRepository:
    def __init__(self, session):
        self.entities = {"entity-1": FakeEntity("entity-1", name="Existing")}

    async def count(self):
        return len(self.entities)

    async def list(self, *, offset=0, limit=100):
        return list(self.entities.values())[offset : offset + limit]

    async def get(self, entity_id):
        return self.entities.get(entity_id)

    async def create(self, values):
        entity = FakeEntity("entity-2", **values)
        self.entities[entity.id] = entity
        return entity

    async def update(self, entity, values):
        for key, value in values.items():
            setattr(entity, key, value)
        return entity

    async def delete(self, entity):
        self.entities.pop(entity.id, None)


class FakeCRUDService(CRUDService):
    repository_cls = FakeRepository
    resource_name = "fake"


async def test_crud_service_create_commits_and_refreshes():
    session = FakeSession()
    service = FakeCRUDService(session)

    entity = await service.create(FakePayload(name="Created"))

    assert entity.id == "entity-2"
    assert entity.name == "Created"
    assert session.committed is True
    assert session.refreshed is True


async def test_crud_service_get_raises_not_found():
    service = FakeCRUDService(FakeSession())

    with pytest.raises(NotFoundError):
        await service.get("missing")
