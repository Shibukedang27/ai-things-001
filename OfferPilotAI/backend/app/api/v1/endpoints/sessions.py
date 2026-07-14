"""Session CRUD endpoints."""

from app.api.crud_router import create_crud_router
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate
from app.services.resources import SessionCRUDService

router = create_crud_router(
    service_cls=SessionCRUDService,
    create_schema=SessionCreate,
    update_schema=SessionUpdate,
    read_schema=SessionRead,
    resource_name="sessions",
)
