"""Interview session endpoints."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_principal
from app.api.crud_router import create_crud_router
from app.schemas.common import APIResponse
from app.schemas.interview import (
    InterviewCreate,
    InterviewRead,
    InterviewSessionCreate,
    InterviewSessionRead,
    InterviewTemplateRead,
    InterviewUpdate,
)
from app.services.interview import InterviewService
from app.services.resources import InterviewCRUDService

router = APIRouter()


@router.get(
    "/templates",
    response_model=APIResponse[list[InterviewTemplateRead]],
    summary="List interview templates",
)
async def list_interview_templates() -> APIResponse[list[InterviewTemplateRead]]:
    service = InterviewService()
    return APIResponse(data=service.list_templates())


@router.post(
    "/sessions",
    response_model=APIResponse[InterviewSessionRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create an interview session draft",
)
async def create_interview_session(
    payload: InterviewSessionCreate,
) -> APIResponse[InterviewSessionRead]:
    service = InterviewService()
    return APIResponse(data=service.create_session(payload))


router.include_router(
    create_crud_router(
        service_cls=InterviewCRUDService,
        create_schema=InterviewCreate,
        update_schema=InterviewUpdate,
        read_schema=InterviewRead,
        resource_name="interviews",
    ),
    dependencies=[Depends(get_current_principal)],
)
