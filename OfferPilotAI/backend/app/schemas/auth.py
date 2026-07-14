"""Authentication API schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.enums import SessionStatus
from app.schemas.common import ORMModel
from app.utils.security import validate_password_strength


class PasswordInputMixin(BaseModel):
    """Shared password validation."""

    password: str = Field(..., min_length=12, max_length=256)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class SignupRequest(PasswordInputMixin):
    """Signup request."""

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=160)

    @field_validator("password")
    @classmethod
    def validate_signup_password(cls, value: str, info) -> str:
        validate_password_strength(value, email=str(info.data.get("email")) if info.data.get("email") else None)
        return value


class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=256)


class RefreshTokenRequest(BaseModel):
    """Refresh-token exchange request."""

    refresh_token: str = Field(..., min_length=32)


class LogoutRequest(BaseModel):
    """Logout request."""

    refresh_token: str | None = Field(default=None, min_length=32)


class ForgotPasswordRequest(BaseModel):
    """Forgot-password request."""

    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Forgot-password response."""

    message: str
    reset_token: str | None = None
    expires_at: datetime | None = None


class ResetPasswordRequest(BaseModel):
    """Password reset request."""

    token: str = Field(..., min_length=32)
    new_password: str = Field(..., min_length=12, max_length=256)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class TokenPair(BaseModel):
    """JWT token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_at: datetime


class RoleRead(ORMModel):
    """Role response."""

    id: str
    name: str
    description: str | None
    permissions: list[str]
    is_system: bool
    created_at: datetime
    updated_at: datetime


class RoleCreate(BaseModel):
    """Role creation request."""

    name: str = Field(..., min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_-]*$")
    description: str | None = Field(default=None, max_length=500)
    permissions: list[str] = Field(default_factory=list, max_length=64)
    is_system: bool = False


class RoleAssignmentRequest(BaseModel):
    """Role assignment request."""

    role_name: str = Field(..., min_length=2, max_length=64)


class UserProfile(BaseModel):
    """Authenticated user profile."""

    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    roles: list[str]
    created_at: datetime
    updated_at: datetime


class ProfileUpdateRequest(BaseModel):
    """Authenticated profile update request."""

    full_name: str | None = Field(default=None, min_length=2, max_length=160)


class AuthResponse(BaseModel):
    """Authentication response."""

    user: UserProfile
    tokens: TokenPair


class SessionSummary(ORMModel):
    """Authenticated session summary."""

    id: str
    status: SessionStatus
    ip_address: str | None
    user_agent: str | None
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    updated_at: datetime
