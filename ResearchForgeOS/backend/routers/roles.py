from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_permissions
from backend.dependencies.database import get_db
from backend.models.permission import Permission
from backend.models.role import Role
from backend.models.user import User
from backend.schemas.role import PermissionRead, RoleCreate, RoleRead, RoleUpdate
from backend.services.role_service import RoleService

router = APIRouter()


@router.get("/permissions", response_model=list[PermissionRead], summary="List permissions")
def list_permissions(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("permissions:read"))],
) -> list[Permission]:
    return list(RoleService(session).list_permissions())


@router.get("", response_model=list[RoleRead], summary="List roles")
def list_roles(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("roles:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[Role]:
    return list(RoleService(session).list_roles(offset=offset, limit=limit))


@router.post("", response_model=RoleRead, status_code=201, summary="Create a role")
def create_role(
    payload: RoleCreate,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("roles:write"))],
) -> Role:
    return RoleService(session).create_role(payload)


@router.get("/{role_id}", response_model=RoleRead, summary="Read a role")
def read_role(
    role_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("roles:read"))],
) -> Role:
    return RoleService(session).get_role(role_id)


@router.patch("/{role_id}", response_model=RoleRead, summary="Update a role")
def update_role(
    role_id: str,
    payload: RoleUpdate,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("roles:write"))],
) -> Role:
    return RoleService(session).update_role(role_id, payload)
