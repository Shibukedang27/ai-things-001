"""Report CRUD endpoints."""

from app.api.crud_router import create_crud_router
from app.schemas.report import ReportCreate, ReportRead, ReportUpdate
from app.services.resources import ReportCRUDService

router = create_crud_router(
    service_cls=ReportCRUDService,
    create_schema=ReportCreate,
    update_schema=ReportUpdate,
    read_schema=ReportRead,
    resource_name="reports",
)
