"""User CRUD endpoints."""

from app.api.crud_router import create_crud_router
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.resources import UserCRUDService

router = create_crud_router(
    service_cls=UserCRUDService,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    read_schema=UserRead,
    resource_name="users",
)
