"""Health endpoint tests."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_health_check_returns_standard_envelope(client):
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "healthy"
    assert payload["data"]["service"] == "OfferPilot AI API"
    assert payload["errors"] == []
    assert response.headers["X-Request-ID"]


async def test_readiness_can_run_without_external_dependencies_in_test_mode(client):
    response = await client.get("/api/v1/health/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["ready"] is True
    assert payload["data"]["dependencies"] == []
