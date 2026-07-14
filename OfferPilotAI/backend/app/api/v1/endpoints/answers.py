"""Answer CRUD endpoints."""

from app.api.crud_router import create_crud_router
from app.schemas.answer import AnswerCreate, AnswerRead, AnswerUpdate
from app.services.resources import AnswerCRUDService

router = create_crud_router(
    service_cls=AnswerCRUDService,
    create_schema=AnswerCreate,
    update_schema=AnswerUpdate,
    read_schema=AnswerRead,
    resource_name="answers",
)
