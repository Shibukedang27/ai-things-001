"""Interview history CRUD endpoints."""

from app.api.crud_router import create_crud_router
from app.schemas.interview_history import InterviewHistoryCreate, InterviewHistoryRead, InterviewHistoryUpdate
from app.services.resources import InterviewHistoryCRUDService

router = create_crud_router(
    service_cls=InterviewHistoryCRUDService,
    create_schema=InterviewHistoryCreate,
    update_schema=InterviewHistoryUpdate,
    read_schema=InterviewHistoryRead,
    resource_name="interview history",
)
