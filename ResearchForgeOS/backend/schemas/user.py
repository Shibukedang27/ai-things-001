from datetime import datetime

from pydantic import EmailStr, Field, SecretStr, field_validator

from backend.schemas.common import APIModel, TimestampedRead
from backend.schemas.role import RoleRead


class UserBase(APIModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserCreate(UserBase):
    password: SecretStr = Field(min_length=12, max_length=128)


class UserUpdate(APIModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)


class UserRead(UserBase, TimestampedRead):
    id: str
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None
    roles: list[RoleRead] = Field(default_factory=list)
