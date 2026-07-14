"""User API schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class UserCreate(BaseModel):
    """Request body for user creation."""

    email: EmailStr = Field(..., max_length=320)
    full_name: str = Field(..., min_length=2, max_length=160)


class UserUpdate(BaseModel):
    """Request body for user updates."""

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    is_active: bool | None = None
    is_verified: bool | None = None


class UserRead(ORMModel):
    """User response."""

    id: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
