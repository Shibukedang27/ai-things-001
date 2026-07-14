"""AI evaluation engine tests."""

import pytest

from app.services.evaluation_provider import EvaluationInput, TemplateAIEvaluationProvider

pytestmark = pytest.mark.asyncio


async def test_evaluation_options_requires_authentication(client):
    response = await client.get("/api/v1/evaluations/options")

    assert response.status_code == 401


async def test_template_evaluator_generates_required_scores_and_outputs():
    provider = TemplateAIEvaluationProvider()

    result = await provider.evaluate(
        EvaluationInput(
            role="Backend Engineer",
            question_prompt="Design a scalable API with database indexes and observability.",
            question_category="system_design",
            question_difficulty="hard",
            answer_transcript=(
                "First, I would define the API boundaries and data model. "
                "Second, I would use database indexes, caching, queues, monitoring, and reliability tradeoffs. "
                "For example, I would track latency and error rate before scaling replicas."
            ),
        )
    )

    assert 0 <= result.technical_accuracy <= 100
    assert 0 <= result.communication <= 100
    assert 0 <= result.completeness <= 100
    assert 0 <= result.confidence_score <= 100
    assert 0 <= result.problem_solving <= 100
    assert 0 <= result.explanation_quality <= 100
    assert 0 <= result.overall_score <= 100
    assert result.correct_answer
    assert result.better_answer
    assert result.industry_standard_answer
    assert result.improvement_suggestions
    assert result.related_topics
    assert result.difficulty_analysis["difficulty"] == "hard"
    assert result.evaluator_version == "template-ai-evaluator-v1"
