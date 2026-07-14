"""Question catalog endpoint tests."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_list_question_categories(client):
    response = await client.get("/api/v1/questions/categories")

    assert response.status_code == 200
    payload = response.json()
    category_ids = {item["id"] for item in payload["data"]}
    assert "technical" in category_ids
    assert "behavioral" in category_ids


async def test_list_difficulty_levels(client):
    response = await client.get("/api/v1/questions/difficulty-levels")

    assert response.status_code == 200
    payload = response.json()
    difficulty_ids = {item["id"] for item in payload["data"]}
    assert difficulty_ids == {"easy", "medium", "hard", "expert"}
