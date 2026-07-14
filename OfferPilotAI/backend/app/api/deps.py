"""Reusable FastAPI dependencies."""

from collections.abc import AsyncGenerator

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.db.session import async_session_factory
from app.services.auth import AuthService, AuthenticatedPrincipal

bearer_scheme = HTTPBearer(auto_error=False)


def get_request_settings(request: Request) -> Settings:
    """Return settings attached to the FastAPI app."""

    return request.app.state.settings


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session per request."""

    async with async_session_factory() as session:
        yield session


async def require_api_key(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """Optional API-key guard for protected future endpoints."""

    settings = get_request_settings(request)
    if not settings.auth_enabled:
        return

    if not settings.api_key:
        raise AuthenticationError("API authentication is enabled but no API key is configured.")

    if x_api_key != settings.api_key:
        raise AuthenticationError("A valid API key is required.")


async def get_current_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> AuthenticatedPrincipal:
    """Authenticate the current user from a Bearer access token."""

    if not credentials or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Bearer access token is required.")

    service = AuthService(session, get_request_settings(request))
    return await service.authenticate_access_token(credentials.credentials)


def require_roles(*required_roles: str):
    """Require the current user to have at least one of the given roles."""

    async def dependency(principal: AuthenticatedPrincipal = Depends(get_current_principal)) -> AuthenticatedPrincipal:
        if not set(required_roles).intersection(principal.roles):
            raise AuthorizationError("Insufficient role permissions.")
        return principal

    return dependency
