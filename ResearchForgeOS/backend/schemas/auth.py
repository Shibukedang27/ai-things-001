from pydantic import EmailStr, Field, SecretStr, field_validator

from backend.schemas.common import APIModel


class LoginRequest(APIModel):
    email: EmailStr
    password: SecretStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class RefreshTokenRequest(APIModel):
    refresh_token: str = Field(min_length=32)


class TokenPair(APIModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
