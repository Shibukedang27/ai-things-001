"""Protected route tests."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_product_crud_routes_require_bearer_token(client):
    response = await client.get("/api/v1/users/")

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "AUTHENTICATION_REQUIRED"


async def test_public_catalog_metadata_remains_available(client):
    response = await client.get("/api/v1/questions/categories")

    assert response.status_code == 200
