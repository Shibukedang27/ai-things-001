from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.dependencies.auth import get_current_active_user, require_permissions
from backend.dependencies.database import get_db
from backend.models.user import User
from backend.schemas.user import UserRead, UserUpdate
from backend.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=list[UserRead], summary="List users")
def list_users(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("users:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[User]:
    return list(UserService(session).list_users(offset=offset, limit=limit))


@router.get("/me", response_model=UserRead, summary="Read my user profile")
def read_my_profile(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user


@router.patch("/me", response_model=UserRead, summary="Update my user profile")
def update_my_profile(
    payload: UserUpdate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return UserService(session).update_user(current_user.id, payload)


@router.get("/{user_id}", response_model=UserRead, summary="Read a user")
def read_user(
    user_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("users:read"))],
) -> User:
    return UserService(session).get_user(user_id)
