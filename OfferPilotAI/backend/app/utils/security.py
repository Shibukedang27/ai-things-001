"""Authentication and cryptography helpers."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
from typing import Any
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from app.core.config import Settings
from app.core.exceptions import AuthenticationError

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2id."""

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against an Argon2 hash."""

    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    """Return whether a password hash should be upgraded."""

    return password_hasher.check_needs_rehash(password_hash)


def create_token_fingerprint(token: str) -> str:
    """Create a deterministic token fingerprint for database storage."""

    return sha256(token.encode("utf-8")).hexdigest()


def create_opaque_token() -> str:
    """Create a URL-safe opaque token."""

    return secrets.token_urlsafe(48)


def create_jti() -> str:
    """Create a JWT ID."""

    return uuid4().hex


def create_jwt(
    *,
    subject: str,
    token_type: str,
    settings: Settings,
    expires_delta: timedelta,
    jti: str | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, datetime, str]:
    """Create a signed JWT and return token, expiry, and JTI."""

    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + expires_delta
    token_jti = jti or create_jti()
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "jti": token_jti,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_at, token_jti


def decode_jwt(token: str, *, settings: Settings, expected_type: str | None = None) -> dict[str, Any]:
    """Decode and validate a signed JWT."""

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid authentication token.") from exc

    if expected_type and payload.get("type") != expected_type:
        raise AuthenticationError("Invalid token type.")

    if not payload.get("sub") or not payload.get("jti"):
        raise AuthenticationError("Invalid authentication token claims.")

    return payload


def validate_password_strength(password: str, *, email: str | None = None) -> None:
    """Raise a validation error if the password is too weak."""

    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long.")
    if not any(character.islower() for character in password):
        raise ValueError("Password must include a lowercase letter.")
    if not any(character.isupper() for character in password):
        raise ValueError("Password must include an uppercase letter.")
    if not any(character.isdigit() for character in password):
        raise ValueError("Password must include a number.")
    if not any(not character.isalnum() for character in password):
        raise ValueError("Password must include a symbol.")
    if email and email.split("@", 1)[0].lower() in password.lower():
        raise ValueError("Password must not contain the email username.")
