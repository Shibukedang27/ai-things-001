"""Authentication endpoints."""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_principal, get_db_session, get_request_settings, require_roles
from app.core.config import Settings
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    ProfileUpdateRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    RoleAssignmentRequest,
    RoleCreate,
    RoleRead,
    SessionSummary,
    SignupRequest,
    TokenPair,
    UserProfile,
)
from app.schemas.common import APIResponse, DeleteResponse
from app.services.auth import AuthService, AuthenticatedPrincipal

router = APIRouter()


def get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> str | None:
    return request.headers.get("User-Agent")


def get_auth_service(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> AuthService:
    settings: Settings = get_request_settings(request)
    return AuthService(session, settings)


@router.post(
    "/signup",
    response_model=APIResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a user account",
)
async def signup(
    payload: SignupRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[AuthResponse]:
    return APIResponse(
        data=await service.signup(
            payload,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    )


@router.post(
    "/login",
    response_model=APIResponse[AuthResponse],
    summary="Authenticate with email and password",
)
async def login(
    payload: LoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[AuthResponse]:
    return APIResponse(
        data=await service.login(
            payload,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenPair],
    summary="Rotate refresh token and issue a new access token",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[TokenPair]:
    return APIResponse(
        data=await service.refresh(
            payload.refresh_token,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    )


@router.post(
    "/logout",
    response_model=APIResponse[dict[str, bool]],
    summary="Logout the current session",
)
async def logout(
    payload: LogoutRequest,
    response: Response,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[dict[str, bool]]:
    await service.logout(principal=principal, refresh_token=payload.refresh_token)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return APIResponse(data={"logged_out": True})


@router.post(
    "/forgot-password",
    response_model=APIResponse[ForgotPasswordResponse],
    summary="Generate password reset instructions",
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[ForgotPasswordResponse]:
    return APIResponse(
        data=await service.forgot_password(
            str(payload.email),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    )


@router.post(
    "/reset-password",
    response_model=APIResponse[dict[str, bool]],
    summary="Reset password with a reset token",
)
async def reset_password(
    payload: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[dict[str, bool]]:
    await service.reset_password(token=payload.token, new_password=payload.new_password)
    return APIResponse(data={"password_reset": True})


@router.get(
    "/me",
    response_model=APIResponse[UserProfile],
    summary="Get current user profile",
)
async def get_profile(
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[UserProfile]:
    return APIResponse(data=await service.build_user_profile(principal.user))


@router.patch(
    "/me",
    response_model=APIResponse[UserProfile],
    summary="Update current user profile",
)
async def update_profile(
    payload: ProfileUpdateRequest,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[UserProfile]:
    return APIResponse(data=await service.update_profile(principal, payload))


@router.get(
    "/sessions",
    response_model=APIResponse[list[SessionSummary]],
    summary="List current user sessions",
)
async def list_sessions(
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[list[SessionSummary]]:
    return APIResponse(data=await service.list_sessions(principal))


@router.delete(
    "/sessions/{session_id}",
    response_model=APIResponse[DeleteResponse],
    summary="Revoke a session",
)
async def revoke_session(
    session_id: str,
    principal: AuthenticatedPrincipal = Depends(get_current_principal),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[DeleteResponse]:
    await service.revoke_session(principal=principal, session_id=session_id)
    return APIResponse(data=DeleteResponse(id=session_id))


@router.get(
    "/roles",
    response_model=APIResponse[list[RoleRead]],
    summary="List roles",
)
async def list_roles(
    _: AuthenticatedPrincipal = Depends(require_roles("admin")),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[list[RoleRead]]:
    return APIResponse(data=await service.list_roles())


@router.post(
    "/roles",
    response_model=APIResponse[RoleRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create role",
)
async def create_role(
    payload: RoleCreate,
    _: AuthenticatedPrincipal = Depends(require_roles("admin")),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[RoleRead]:
    return APIResponse(data=await service.create_role(payload))


@router.post(
    "/users/{user_id}/roles",
    response_model=APIResponse[UserProfile],
    summary="Assign role to user",
)
async def assign_role(
    user_id: str,
    payload: RoleAssignmentRequest,
    principal: AuthenticatedPrincipal = Depends(require_roles("admin")),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[UserProfile]:
    return APIResponse(
        data=await service.assign_role(
            user_id=user_id,
            role_name=payload.role_name,
            assigned_by_user_id=principal.user.id,
        )
    )


@router.delete(
    "/users/{user_id}/roles/{role_name}",
    response_model=APIResponse[UserProfile],
    summary="Remove role from user",
)
async def remove_role(
    user_id: str,
    role_name: str,
    _: AuthenticatedPrincipal = Depends(require_roles("admin")),
    service: AuthService = Depends(get_auth_service),
) -> APIResponse[UserProfile]:
    return APIResponse(data=await service.remove_role(user_id=user_id, role_name=role_name))
