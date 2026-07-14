"""Learning recommendation engine tests."""

from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services.recommendation_provider import CatalogLearningRecommendationProvider, RecommendationInput

pytestmark = pytest.mark.asyncio


async def test_recommendation_options_requires_authentication(client):
    response = await client.get("/api/v1/recommendations/options")

    assert response.status_code == 401


async def test_recommendation_provider_generates_resources_and_roadmaps():
    provider = CatalogLearningRecommendationProvider()
    evaluation = SimpleNamespace(
        overall_score=Decimal("58.00"),
        technical_accuracy=Decimal("52.00"),
        communication=Decimal("81.00"),
        completeness=Decimal("63.00"),
        confidence_score=Decimal("74.00"),
        problem_solving=Decimal("57.00"),
        explanation_quality=Decimal("80.00"),
    )
    question = SimpleNamespace(category="system_design")
    interview = SimpleNamespace(role_title="Backend Engineer")

    plan = await provider.generate(
        RecommendationInput(
            target_role="Backend Engineer",
            estimated_weeks=4,
            evaluation_context=[(evaluation, question, interview)],
            history=[],
        )
    )

    assert plan.weak_topics[0].topic == "System Design"
    assert plan.weak_topics[0].priority == "high"
    assert plan.leetcode_problems
    assert plan.hackerrank_problems
    assert plan.books
    assert plan.courses
    assert plan.youtube_videos
    assert len(plan.daily_practice_plan) == 7
    assert len(plan.weekly_roadmap) == 4
    assert len(plan.monthly_roadmap) == 3
    assert plan.source_summary["evaluations_analyzed"] == 1
