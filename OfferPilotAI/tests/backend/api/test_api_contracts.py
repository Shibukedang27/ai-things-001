"""REST API contract and middleware tests."""

import pytest

pytestmark = [pytest.mark.api, pytest.mark.asyncio]


@pytest.mark.parametrize(
    ("path", "expected_keys"),
    [
        ("/", {"service", "version", "docs"}),
        ("/api/v1/health", {"status", "service", "version"}),
        ("/api/v1/health/live", {"status"}),
        ("/api/v1/questions/categories", None),
        ("/api/v1/questions/difficulty-levels", None),
        ("/api/v1/interviews/templates", None),
        ("/api/v1/interview-engine/options", {"roles_note", "difficulties", "categories", "duration_minutes"}),
    ],
)
async def test_public_get_contracts_return_standard_response(client, path, expected_keys):
    response = await client.get(path, headers={"X-Request-ID": "contract-test-request"})

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) >= {"data", "meta", "errors"}
    assert payload["errors"] == []
    if expected_keys:
        assert set(payload["data"]) >= expected_keys


async def test_middleware_adds_request_context_and_security_headers(client):
    response = await client.get("/api/v1/health/live", headers={"X-Request-ID": "api-contract-1"})

    assert response.headers["X-Request-ID"] == "api-contract-1"
    assert "X-Process-Time-Ms" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/analytics/overview",
        "/api/v1/evaluations/options",
        "/api/v1/recommendations/options",
        "/api/v1/live-coding/options",
        "/api/v1/resume-analyzer/options",
        "/api/v1/users/",
        "/api/v1/answers/",
        "/api/v1/reports/",
        "/api/v1/learning-roadmaps/",
        "/api/v1/leaderboard/",
        "/api/v1/sessions/",
        "/api/v1/interview-history/",
    ],
)
async def test_protected_get_contracts_require_bearer_token(client, path):
    response = await client.get(path)

    assert response.status_code == 401
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "AUTHENTICATION_REQUIRED"


async def test_openapi_documents_all_product_api_surfaces(client):
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    expected_paths = {
        "/api/v1/analytics/overview",
        "/api/v1/auth/signup",
        "/api/v1/auth/login",
        "/api/v1/auth/logout",
        "/api/v1/auth/refresh",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
        "/api/v1/auth/me",
        "/api/v1/interview-engine/options",
        "/api/v1/interview-engine/sessions",
        "/api/v1/interview-engine/sessions/{interview_id}",
        "/api/v1/interview-engine/sessions/{interview_id}/current-question",
        "/api/v1/interview-engine/sessions/{interview_id}/answers",
        "/api/v1/interview-engine/sessions/{interview_id}/complete",
        "/api/v1/evaluations/options",
        "/api/v1/evaluations/answers/{answer_id}",
        "/api/v1/evaluations/interviews/{interview_id}",
        "/api/v1/recommendations/options",
        "/api/v1/recommendations/roadmaps",
        "/api/v1/recommendations/roadmaps/latest",
        "/api/v1/live-coding/options",
        "/api/v1/live-coding/run",
        "/api/v1/live-coding/analyze",
        "/api/v1/live-coding/submissions",
        "/api/v1/live-coding/submissions/{submission_id}",
        "/api/v1/resume-analyzer/options",
        "/api/v1/resume-analyzer/analyze",
        "/api/v1/resume-analyzer/analyze-text",
        "/api/v1/resume-analyzer/analyses",
        "/api/v1/resume-analyzer/analyses/{analysis_id}",
    }
    assert expected_paths.issubset(paths)
