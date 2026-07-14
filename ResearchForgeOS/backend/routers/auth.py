from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.dependencies.auth import get_current_active_user
from backend.dependencies.database import get_db
from backend.models.user import User
from backend.schemas.auth import LoginRequest, RefreshTokenRequest, TokenPair
from backend.schemas.user import UserCreate, UserRead
from backend.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Register a user")
def register(payload: UserCreate, session: Annotated[Session, Depends(get_db)]) -> User:
    return AuthService(session).register_user(payload)


@router.post("/login", response_model=TokenPair, summary="Issue access and refresh tokens")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_db)],
) -> TokenPair:
    service = AuthService(session)
    user = service.authenticate_user(form_data.username, form_data.password)
    return service.issue_tokens(user)


@router.post("/login/json", response_model=TokenPair, summary="Issue tokens with a JSON payload")
def login_json(payload: LoginRequest, session: Annotated[Session, Depends(get_db)]) -> TokenPair:
    service = AuthService(session)
    user = service.authenticate_user(payload.email, payload.password.get_secret_value())
    return service.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair, summary="Refresh an access token")
def refresh(payload: RefreshTokenRequest, session: Annotated[Session, Depends(get_db)]) -> TokenPair:
    return AuthService(session).refresh_tokens(payload.refresh_token)


@router.get("/me", response_model=UserRead, summary="Read the authenticated user")
def me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user
