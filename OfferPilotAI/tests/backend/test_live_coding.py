"""Live coding module tests."""

import pytest

from app.domain.enums import CodeRunStatus, CodingLanguage
from app.services.coding_analysis import CodeAnalysisInput, HeuristicCodeAnalysisProvider
from app.services.coding_execution import CodeExecutionInput, CodeExecutionService

pytestmark = pytest.mark.asyncio


async def test_live_coding_routes_require_authentication(client):
    response = await client.get("/api/v1/live-coding/options")

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "AUTHENTICATION_REQUIRED"


async def test_python_runner_executes_code_with_stdin():
    service = CodeExecutionService()

    result = await service.execute(
        CodeExecutionInput(
            language=CodingLanguage.PYTHON,
            source_code="values = [int(value) for value in input().split()]\nprint(sum(values))\n",
            stdin="2 3 5",
            timeout_seconds=3,
        )
    )

    assert result.status == CodeRunStatus.SUCCESS
    assert result.stdout.strip() == "10"
    assert result.exit_code == 0


async def test_sql_runner_returns_select_rows():
    service = CodeExecutionService()

    result = await service.execute(
        CodeExecutionInput(
            language=CodingLanguage.SQL,
            source_code=(
                "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);\n"
                "INSERT INTO users (name) VALUES ('Avery'), ('Maya');\n"
                "SELECT name FROM users ORDER BY id;\n"
            ),
            stdin="",
            timeout_seconds=3,
        )
    )

    assert result.status == CodeRunStatus.SUCCESS
    assert "Avery" in result.stdout
    assert "Maya" in result.stdout


async def test_analyzer_detects_nested_complexity_and_generates_optimized_code():
    provider = HeuristicCodeAnalysisProvider()

    result = await provider.analyze(
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
            prompt="Return indices of two numbers that add up to target.",
        )
    )

    assert result.time_complexity == "O(n^2)"
    assert result.space_complexity == "O(1)"
    assert result.optimized_code
    assert "seen" in result.optimized_code
    assert result.improvement_suggestions
    assert result.quality_score <= 100


async def test_analyzer_reports_python_correctness_bugs():
    provider = HeuristicCodeAnalysisProvider()

    result = await provider.analyze(
        CodeAnalysisInput(
            language=CodingLanguage.PYTHON,
            source_code="def divide(value):\n    return value / 0\n",
        )
    )

    assert any(issue.rule == "python.division_by_zero" for issue in result.bugs)
    assert any(issue.severity == "error" for issue in result.bugs)
