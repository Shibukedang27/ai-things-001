"""OpenAPI documentation tests."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_openapi_schema_is_available(client):
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["info"]["title"] == "OfferPilot AI API"
    assert "/api/v1/health" in payload["paths"]
    assert "/api/v1/auth/signup" in payload["paths"]
    assert "/api/v1/auth/login" in payload["paths"]
    assert "/api/v1/auth/logout" in payload["paths"]
    assert "/api/v1/auth/refresh" in payload["paths"]
    assert "/api/v1/auth/forgot-password" in payload["paths"]
    assert "/api/v1/auth/reset-password" in payload["paths"]
    assert "/api/v1/auth/me" in payload["paths"]
    assert "/api/v1/auth/roles" in payload["paths"]
    assert "/api/v1/interview-engine/options" in payload["paths"]
    assert "/api/v1/interview-engine/sessions" in payload["paths"]
    assert "/api/v1/interview-engine/sessions/{interview_id}/answers" in payload["paths"]
    assert "/api/v1/interview-engine/sessions/{interview_id}/complete" in payload["paths"]
    assert "/api/v1/evaluations/options" in payload["paths"]
    assert "/api/v1/evaluations/answers/{answer_id}" in payload["paths"]
    assert "/api/v1/evaluations/interviews/{interview_id}" in payload["paths"]
    assert "/api/v1/recommendations/options" in payload["paths"]
    assert "/api/v1/recommendations/roadmaps" in payload["paths"]
    assert "/api/v1/recommendations/roadmaps/latest" in payload["paths"]
    assert "/api/v1/interviews/sessions" in payload["paths"]
    assert "/api/v1/users/" in payload["paths"]
    assert "/api/v1/questions/" in payload["paths"]
    assert "/api/v1/answers/" in payload["paths"]
    assert "/api/v1/reports/" in payload["paths"]
    assert "/api/v1/learning-roadmaps/" in payload["paths"]
    assert "/api/v1/leaderboard/" in payload["paths"]
    assert "/api/v1/sessions/" in payload["paths"]
    assert "/api/v1/interview-history/" in payload["paths"]
