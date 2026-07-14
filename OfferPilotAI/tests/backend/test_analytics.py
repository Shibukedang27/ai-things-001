"""Analytics tests."""

from datetime import timedelta
from decimal import Decimal

import pytest

from app.domain.enums import InterviewStatus, InterviewType
from app.models import Interview
from app.services.analytics import AnalyticsAggregationService, EvaluationAnalyticsRecord
from app.utils.time import utc_now


@pytest.mark.asyncio
async def test_analytics_route_requires_authentication(client):
    response = await client.get("/api/v1/analytics/overview")

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "AUTHENTICATION_REQUIRED"


def test_analytics_overview_generates_all_requested_views():
    now = utc_now()
    records = [
        EvaluationAnalyticsRecord(
            category="python",
            created_at=now - timedelta(days=14),
            overall_score=Decimal("72"),
            technical_accuracy=Decimal("70"),
            communication=Decimal("76"),
            problem_solving=Decimal("71"),
            explanation_quality=Decimal("74"),
        ),
        EvaluationAnalyticsRecord(
            category="python",
            created_at=now - timedelta(days=7),
            overall_score=Decimal("84"),
            technical_accuracy=Decimal("86"),
            communication=Decimal("82"),
            problem_solving=Decimal("85"),
            explanation_quality=Decimal("83"),
        ),
        EvaluationAnalyticsRecord(
            category="system_design",
            created_at=now - timedelta(days=2),
            overall_score=Decimal("91"),
            technical_accuracy=Decimal("93"),
            communication=Decimal("88"),
            problem_solving=Decimal("92"),
            explanation_quality=Decimal("90"),
        ),
    ]
    interviews = [
        Interview(
            id="interview-1",
            user_id="user-1",
            title="Backend Mock",
            role_title="Backend Engineer",
            interview_type=InterviewType.TECHNICAL.value,
            status=InterviewStatus.COMPLETED.value,
            duration_minutes=45,
            overall_score=Decimal("84"),
            completed_at=now - timedelta(days=7),
        ),
        Interview(
            id="interview-2",
            user_id="user-1",
            title="Architecture Mock",
            role_title="Staff Engineer",
            interview_type=InterviewType.SYSTEM_DESIGN.value,
            status=InterviewStatus.COMPLETED.value,
            duration_minutes=60,
            overall_score=Decimal("91"),
            completed_at=now - timedelta(days=2),
        ),
    ]

    service = AnalyticsAggregationService.__new__(AnalyticsAggregationService)
    overview = service.build_overview(records=records, interviews=interviews)

    assert overview.summary.average_score == Decimal("82.33")
    assert overview.summary.highest_score == Decimal("91")
    assert overview.summary.interview_count == 2
    assert overview.topic_wise_accuracy
    assert overview.weekly_progress
    assert overview.monthly_progress
    assert len(overview.heat_map) == 35
    assert len(overview.radar_chart) == 5
    assert overview.weakness_trends
    assert overview.strength_trends
    assert len(overview.interview_history) == 2
    assert len(overview.performance_graphs) == 3
