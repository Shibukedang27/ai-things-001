"""Interview engine tests."""

import pytest

from app.domain.enums import DifficultyLevel
from app.schemas.interview_engine import EngineQuestionCategory
from app.services.question_generation import TemplateAIQuestionGenerator

pytestmark = pytest.mark.asyncio


async def test_interview_engine_options_include_requested_categories(client):
    response = await client.get("/api/v1/interview-engine/options")

    assert response.status_code == 200
    categories = set(response.json()["data"]["categories"])
    assert categories == {
        "python",
        "java",
        "sql",
        "dsa",
        "system_design",
        "machine_learning",
        "deep_learning",
        "nlp",
        "prompt_engineering",
        "behavioral",
        "hr",
    }


async def test_start_interview_requires_authentication(client):
    response = await client.post(
        "/api/v1/interview-engine/sessions",
        json={
            "role": "Backend Engineer",
            "difficulty": "medium",
            "duration_minutes": 30,
            "categories": ["python", "sql"],
        },
    )

    assert response.status_code == 401


async def test_template_question_generator_cycles_categories():
    generator = TemplateAIQuestionGenerator()

    questions = await generator.generate(
        role="Machine Learning Engineer",
        difficulty=DifficultyLevel.HARD,
        categories=[
            EngineQuestionCategory.PYTHON,
            EngineQuestionCategory.MACHINE_LEARNING,
            EngineQuestionCategory.SYSTEM_DESIGN,
        ],
        question_count=5,
    )

    assert len(questions) == 5
    assert [question.category for question in questions[:3]] == [
        EngineQuestionCategory.PYTHON,
        EngineQuestionCategory.MACHINE_LEARNING,
        EngineQuestionCategory.SYSTEM_DESIGN,
    ]
    assert all(question.difficulty == DifficultyLevel.HARD for question in questions)
    assert all("Machine Learning Engineer" in question.prompt for question in questions)
