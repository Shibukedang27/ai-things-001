"""Reusable CRUD router factory."""

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.common import APIResponse, DeleteResponse
from app.services.crud import CRUDService


def create_crud_router(
    *,
    service_cls: type[CRUDService],
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    resource_name: str,
) -> APIRouter:
    """Create a standard CRUD router for one resource."""

    router = APIRouter()
    list_response_model = APIResponse[list[read_schema]]  # type: ignore[valid-type]
    item_response_model = APIResponse[read_schema]  # type: ignore[valid-type]
    operation_slug = resource_name.lower().replace(" ", "_").replace("-", "_")

    async def get_service(session: AsyncSession = Depends(get_db_session)) -> CRUDService:
        return service_cls(session)

    @router.get(
        "/",
        response_model=list_response_model,
        summary=f"List {resource_name}",
        operation_id=f"list_{operation_slug}",
    )
    async def list_items(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=25, ge=1, le=100),
        service: CRUDService = Depends(get_service),
    ) -> APIResponse[list[Any]]:
        items, total = await service.list(page=page, page_size=page_size)
        return APIResponse(
            data=list(items),
            meta={
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                }
            },
        )

    @router.post(
        "/",
        response_model=item_response_model,
        status_code=status.HTTP_201_CREATED,
        summary=f"Create {resource_name}",
        operation_id=f"create_{operation_slug}",
    )
    async def create_item(
        payload: create_schema,  # type: ignore[valid-type]
        service: CRUDService = Depends(get_service),
    ) -> APIResponse[Any]:
        return APIResponse(data=await service.create(payload))

    @router.get(
        "/{entity_id}",
        response_model=item_response_model,
        summary=f"Get {resource_name}",
        operation_id=f"get_{operation_slug}",
    )
    async def get_item(
        entity_id: str,
        service: CRUDService = Depends(get_service),
    ) -> APIResponse[Any]:
        return APIResponse(data=await service.get(entity_id))

    @router.patch(
        "/{entity_id}",
        response_model=item_response_model,
        summary=f"Update {resource_name}",
        operation_id=f"update_{operation_slug}",
    )
    async def update_item(
        entity_id: str,
        payload: update_schema,  # type: ignore[valid-type]
        service: CRUDService = Depends(get_service),
    ) -> APIResponse[Any]:
        return APIResponse(data=await service.update(entity_id, payload))

    @router.delete(
        "/{entity_id}",
        response_model=APIResponse[DeleteResponse],
        summary=f"Delete {resource_name}",
        operation_id=f"delete_{operation_slug}",
    )
    async def delete_item(
        entity_id: str,
        service: CRUDService = Depends(get_service),
    ) -> APIResponse[DeleteResponse]:
        await service.delete(entity_id)
        return APIResponse(data=DeleteResponse(id=entity_id))

    return router
