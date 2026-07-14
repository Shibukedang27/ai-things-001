from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.dependencies.database import get_db
from backend.exceptions import AuthenticationError
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.security.jwt import TokenType, decode_token
from backend.security.permissions import assert_permissions

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    payload = decode_token(token, expected_type=TokenType.ACCESS)
    user = UserRepository(session).get_with_roles(payload.subject)
    if user is None:
        raise AuthenticationError("Authenticated user was not found.")
    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_active:
        raise AuthenticationError("This account is inactive.")
    return current_user


def require_permissions(*permissions: str) -> Callable[[User], User]:
    def dependency(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        assert_permissions(current_user, permissions)
        return current_user

    return dependency
