"""Question catalog endpoints."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_principal
from app.api.crud_router import create_crud_router
from app.schemas.common import APIResponse
from app.schemas.question import DifficultyLevelRead, QuestionCategoryRead, QuestionCreate, QuestionRead, QuestionUpdate
from app.services.question import QuestionCatalogService
from app.services.resources import QuestionCRUDService

router = APIRouter()


@router.get(
    "/categories",
    response_model=APIResponse[list[QuestionCategoryRead]],
    summary="List supported question categories",
)
async def list_question_categories() -> APIResponse[list[QuestionCategoryRead]]:
    service = QuestionCatalogService()
    return APIResponse(data=service.list_categories())


@router.get(
    "/difficulty-levels",
    response_model=APIResponse[list[DifficultyLevelRead]],
    summary="List supported difficulty levels",
)
async def list_difficulty_levels() -> APIResponse[list[DifficultyLevelRead]]:
    service = QuestionCatalogService()
    return APIResponse(data=service.list_difficulty_levels())


router.include_router(
    create_crud_router(
        service_cls=QuestionCRUDService,
        create_schema=QuestionCreate,
        update_schema=QuestionUpdate,
        read_schema=QuestionRead,
        resource_name="questions",
    ),
    dependencies=[Depends(get_current_principal)],
)
