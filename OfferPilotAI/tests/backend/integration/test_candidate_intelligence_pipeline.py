"""Cross-module candidate intelligence integration tests."""

from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.domain.enums import CodingLanguage, DifficultyLevel
from app.schemas.interview_engine import EngineQuestionCategory
from app.services.coding_analysis import CodeAnalysisInput, HeuristicCodeAnalysisProvider
from app.services.evaluation_provider import EvaluationInput, TemplateAIEvaluationProvider
from app.services.question_generation import TemplateAIQuestionGenerator
from app.services.recommendation_provider import CatalogLearningRecommendationProvider, RecommendationInput
from app.services.resume_provider import HeuristicResumeAnalyzerProvider, ResumeAnalyzerInput

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_question_evaluation_recommendation_resume_and_code_pipeline():
    questions = await TemplateAIQuestionGenerator().generate(
        role="Backend Engineer",
        difficulty=DifficultyLevel.HARD,
        categories=[EngineQuestionCategory.PYTHON, EngineQuestionCategory.SYSTEM_DESIGN],
        question_count=2,
    )

    evaluation = await TemplateAIEvaluationProvider().evaluate(
        EvaluationInput(
            role="Backend Engineer",
            question_prompt=questions[0].prompt,
            question_category=questions[0].category.value,
            question_difficulty=questions[0].difficulty.value,
            answer_transcript=(
                "First I would clarify assumptions, then discuss complexity, testing, latency, "
                "monitoring, and tradeoffs. For example, I would validate the API with pytest and "
                "track reliability before adding optimizations."
            ),
        )
    )
    recommendation = await CatalogLearningRecommendationProvider().generate(
        RecommendationInput(
            target_role="Backend Engineer",
            estimated_weeks=4,
            evaluation_context=[
                (
                    SimpleNamespace(
                        overall_score=Decimal("62.00"),
                        technical_accuracy=Decimal("55.00"),
                        communication=Decimal("72.00"),
                        completeness=Decimal("64.00"),
                        confidence_score=Decimal("66.00"),
                        problem_solving=Decimal("58.00"),
                        explanation_quality=Decimal("70.00"),
                    ),
                    SimpleNamespace(category=questions[0].category.value),
                    SimpleNamespace(role_title="Backend Engineer"),
                )
            ],
            history=[],
        )
    )
    code_analysis = await HeuristicCodeAnalysisProvider().analyze(
        CodeAnalysisInput(
            language=CodingLanguage.PYTHON,
            source_code=(
                "def two_sum(nums, target):\n"
                "    for i in range(len(nums)):\n"
                "        for j in range(i + 1, len(nums)):\n"
                "            if nums[i] + nums[j] == target:\n"
                "                return [i, j]\n"
                "    return []\n"
            ),
            prompt="Return indices of two values that add to target.",
        )
    )
    resume_analysis = await HeuristicResumeAnalyzerProvider().analyze(
        ResumeAnalyzerInput(
            filename="backend-engineer.pdf",
            resume_text=(
                "Backend Engineer with Python, FastAPI, PostgreSQL, Docker, testing, monitoring, "
                "system design, and leadership experience. Built APIs and improved latency by 30%."
            ),
            job_description="Python SQL System Design Kubernetes Observability Security",
        )
    )

    assert questions[0].category == EngineQuestionCategory.PYTHON
    assert evaluation.overall_score > 0
    assert recommendation.weak_topics
    assert recommendation.daily_practice_plan
    assert code_analysis.time_complexity == "O(n^2)"
    assert "seen" in code_analysis.optimized_code
    assert resume_analysis.ats_score > 0
    assert resume_analysis.skill_gap_report.recommended_focus
