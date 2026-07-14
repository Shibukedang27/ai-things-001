"""Resume analyzer tests."""

import pytest

from app.services.resume_provider import HeuristicResumeAnalyzerProvider, ResumeAnalyzerInput

pytestmark = pytest.mark.asyncio


async def test_resume_analyzer_routes_require_authentication(client):
    response = await client.get("/api/v1/resume-analyzer/options")

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "AUTHENTICATION_REQUIRED"


async def test_resume_provider_extracts_skills_and_gap_report():
    provider = HeuristicResumeAnalyzerProvider()

    result = await provider.analyze(
        ResumeAnalyzerInput(
            filename="candidate.pdf",
            resume_text=(
                "Senior Backend Engineer. Summary: built Python FastAPI services with PostgreSQL SQL queries, "
                "Docker containers, AWS infrastructure, monitoring and tracing. Experience: led a team, "
                "improved latency by 35%, automated testing with pytest, and documented system design tradeoffs."
            ),
            job_description=(
                "We need a senior engineer with Python, SQL, AWS, Kubernetes, observability, security, "
                "CI/CD, and system design experience."
            ),
        )
    )

    extracted_names = {skill.name for skill in result.extracted_skills}
    missing_names = {skill.name for skill in result.missing_skills}

    assert {"Python", "SQL", "AWS", "Docker", "Testing", "Observability"}.issubset(extracted_names)
    assert "Kubernetes" in missing_names
    assert "Security" in missing_names
    assert result.ats_score > 50
    assert result.resume_suggestions
    assert result.interview_questions
    assert result.skill_gap_report.match_rate > 0
    assert result.analyzer_version == "heuristic-resume-analyzer-v1"


async def test_resume_provider_handles_no_job_description():
    provider = HeuristicResumeAnalyzerProvider()

    result = await provider.analyze(
        ResumeAnalyzerInput(
            filename="candidate.pdf",
            resume_text=(
                "Machine Learning Engineer with Python, SQL, NLP, deep learning, TensorFlow, communication, "
                "and leadership experience. Built models that improved routing accuracy by 18%."
            ),
            job_description=None,
        )
    )

    assert result.extracted_skills
    assert result.missing_skills == []
    assert result.matched_skills == result.extracted_skills
    assert result.ats_score > 50
