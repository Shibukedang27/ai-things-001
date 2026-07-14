"""Security helper tests."""

from datetime import timedelta

import pytest

from app.core.config import Environment, Settings
from app.core.exceptions import AuthenticationError
from app.utils.security import (
    create_jwt,
    create_token_fingerprint,
    decode_jwt,
    hash_password,
    validate_password_strength,
    verify_password,
)


def test_password_hashing_and_verification():
    password_hash = hash_password("StrongPassword!2026")

    assert password_hash != "StrongPassword!2026"
    assert verify_password("StrongPassword!2026", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_password_strength_validation_rejects_weak_password():
    with pytest.raises(ValueError):
        validate_password_strength("weak")


def test_jwt_create_and_decode_validates_type():
    settings = Settings(environment=Environment.TEST, jwt_secret_key="test-secret-with-at-least-32-bytes")
    token, _, jti = create_jwt(
        subject="user-1",
        token_type="access",
        settings=settings,
        expires_delta=timedelta(minutes=5),
    )

    payload = decode_jwt(token, settings=settings, expected_type="access")

    assert payload["sub"] == "user-1"
    assert payload["jti"] == jti

    with pytest.raises(AuthenticationError):
        decode_jwt(token, settings=settings, expected_type="refresh")


def test_token_fingerprint_is_deterministic_and_non_plaintext():
    first = create_token_fingerprint("token")
    second = create_token_fingerprint("token")

    assert first == second
    assert first != "token"
    assert len(first) == 64
