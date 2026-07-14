"""Interview endpoint tests."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_list_interview_templates(client):
    response = await client.get("/api/v1/interviews/templates")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["data"]) >= 3
    assert {template["id"] for template in payload["data"]} >= {"technical-backend", "system-design"}


async def test_create_interview_session_draft(client):
    response = await client.post(
        "/api/v1/interviews/sessions",
        json={
            "role_title": "Senior Backend Engineer",
            "company_name": "Acme AI",
            "seniority": "senior",
            "interview_type": "technical",
            "focus_areas": ["FastAPI", "System Design"],
            "duration_minutes": 60,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["data"]["id"].startswith("int_")
    assert payload["data"]["status"] == "draft"
    assert payload["data"]["question_count"] >= 3


async def test_create_interview_session_rejects_duplicate_focus_areas(client):
    response = await client.post(
        "/api/v1/interviews/sessions",
        json={
            "role_title": "Backend Engineer",
            "focus_areas": ["APIs", "apis"],
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["errors"][0]["code"] == "VALIDATION_ERROR"
