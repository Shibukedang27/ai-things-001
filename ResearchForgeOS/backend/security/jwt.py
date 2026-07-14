from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum
from uuid import uuid4

import jwt
from jwt import InvalidTokenError

from backend.config import get_settings
from backend.exceptions import AuthenticationError
from backend.utils.datetime import utc_now


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class TokenPayload:
    subject: str
    token_type: TokenType
    roles: tuple[str, ...]
    permissions: tuple[str, ...]
    token_id: str


def create_token_pair(*, subject: str, roles: list[str], permissions: list[str]) -> tuple[str, str, int]:
    settings = get_settings()
    access_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_expires = timedelta(days=settings.refresh_token_expire_days)
    access_token = create_token(
        subject=subject,
        token_type=TokenType.ACCESS,
        expires_delta=access_expires,
        roles=roles,
        permissions=permissions,
    )
    refresh_token = create_token(
        subject=subject,
        token_type=TokenType.REFRESH,
        expires_delta=refresh_expires,
        roles=roles,
        permissions=[],
    )
    return access_token, refresh_token, int(access_expires.total_seconds())


def create_token(
    *,
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    roles: list[str],
    permissions: list[str],
) -> str:
    settings = get_settings()
    now = utc_now()
    payload = {
        "sub": subject,
        "type": token_type.value,
        "roles": roles,
        "permissions": permissions,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, *, expected_type: TokenType) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except InvalidTokenError as exc:
        raise AuthenticationError("Token is invalid or expired.") from exc

    token_type = payload.get("type")
    subject = payload.get("sub")
    if token_type != expected_type.value or not subject:
        raise AuthenticationError("Token type or subject is invalid.")

    return TokenPayload(
        subject=str(subject),
        token_type=expected_type,
        roles=tuple(payload.get("roles", [])),
        permissions=tuple(payload.get("permissions", [])),
        token_id=str(payload.get("jti", "")),
    )
