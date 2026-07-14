"""Authentication API and security-boundary tests."""

import pytest

pytestmark = [pytest.mark.auth, pytest.mark.asyncio]


async def test_signup_validates_email_name_and_password_strength(client):
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "not-an-email",
            "full_name": "A",
            "password": "weak",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["data"] is None
    assert {error["code"] for error in payload["errors"]} == {"VALIDATION_ERROR"}


async def test_login_rejects_invalid_email_shape_before_database_work(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "invalid-email", "password": "anything"},
    )

    assert response.status_code == 422
    assert response.json()["errors"][0]["code"] == "VALIDATION_ERROR"


async def test_refresh_token_requires_token_entropy(client):
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "short"})

    assert response.status_code == 422
    assert response.json()["errors"][0]["field"] == "refresh_token"


async def test_profile_route_requires_bearer_access_token(client):
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["errors"][0]["message"] == "Bearer access token is required."


async def test_profile_route_rejects_malformed_bearer_token(client):
    response = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "AUTHENTICATION_REQUIRED"


async def test_admin_role_routes_are_protected(client):
    response = await client.get("/api/v1/auth/roles")

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "AUTHENTICATION_REQUIRED"
