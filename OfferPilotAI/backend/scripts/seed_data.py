"""Seed OfferPilot AI development data.

Run after applying Alembic migrations:

    python backend/scripts/seed_data.py
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
import sys
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import async_session_factory  # noqa: E402
from app.domain.enums import (  # noqa: E402
    CodeRunStatus,
    CodingLanguage,
    DifficultyLevel,
    InterviewHistoryEvent,
    InterviewStatus,
    InterviewType,
    LeaderboardPeriod,
    QuestionCategory,
    ReportStatus,
    RoadmapStatus,
    SeniorityLevel,
    SessionStatus,
)
from app.models import (  # noqa: E402
    Answer,
    AuthCredential,
    CodeSubmission,
    Interview,
    InterviewHistory,
    Leaderboard,
    LearningRoadmap,
    RefreshToken,
    Question,
    Report,
    ResumeAnalysis,
    Role,
    Session,
    User,
    UserRole,
)
from app.utils.security import create_token_fingerprint, hash_password  # noqa: E402
from app.utils.time import utc_now  # noqa: E402


async def upsert(session: AsyncSession, model: type, entity_id: str, values: dict[str, Any]) -> None:
    """Create or update one seed entity by primary key."""

    entity = await session.get(model, entity_id)
    if entity is None:
        session.add(model(id=entity_id, **values))
    else:
        for key, value in values.items():
            setattr(entity, key, value)

    await session.flush()


async def seed() -> None:
    """Seed a representative development dataset."""

    now = utc_now()

    user_id = "00000000-0000-4000-8000-000000000001"
    interview_id = "00000000-0000-4000-8000-000000000101"
    question_id = "00000000-0000-4000-8000-000000000201"
    answer_id = "00000000-0000-4000-8000-000000000301"
    report_id = "00000000-0000-4000-8000-000000000401"
    roadmap_id = "00000000-0000-4000-8000-000000000501"
    leaderboard_id = "00000000-0000-4000-8000-000000000601"
    session_id = "00000000-0000-4000-8000-000000000701"
    history_id = "00000000-0000-4000-8000-000000000801"
    credential_id = "00000000-0000-4000-8000-000000000901"
    user_role_id = "00000000-0000-4000-8000-000000001001"
    refresh_token_id = "00000000-0000-4000-8000-000000001101"
    code_submission_id = "00000000-0000-4000-8000-000000001201"
    resume_analysis_id = "00000000-0000-4000-8000-000000001301"
    user_role_system_id = "00000000-0000-4000-8000-000000010001"
    admin_role_system_id = "00000000-0000-4000-8000-000000010002"

    async with async_session_factory() as session:
        await upsert(
            session,
            User,
            user_id,
            {
                "email": "candidate@example.com",
                "full_name": "Avery Candidate",
                "is_active": True,
                "is_verified": True,
            },
        )

        await upsert(
            session,
            Role,
            user_role_system_id,
            {
                "name": "user",
                "description": "Standard OfferPilot AI user",
                "permissions": ["profile:read", "profile:update", "interviews:manage"],
                "is_system": True,
            },
        )

        await upsert(
            session,
            Role,
            admin_role_system_id,
            {
                "name": "admin",
                "description": "OfferPilot AI administrator",
                "permissions": ["*"],
                "is_system": True,
            },
        )

        await upsert(
            session,
            AuthCredential,
            credential_id,
            {
                "user_id": user_id,
                "password_hash": hash_password("OfferPilotAI!2026"),
                "password_changed_at": now,
                "failed_login_attempts": 0,
                "locked_until": None,
                "last_login_at": None,
                "requires_password_reset": False,
            },
        )

        await upsert(
            session,
            UserRole,
            user_role_id,
            {
                "user_id": user_id,
                "role_id": user_role_system_id,
                "assigned_by_user_id": None,
            },
        )

        await upsert(
            session,
            Interview,
            interview_id,
            {
                "user_id": user_id,
                "title": "Senior Backend Engineer Practice",
                "role_title": "Senior Backend Engineer",
                "company_name": "OfferPilot AI Demo",
                "seniority": SeniorityLevel.SENIOR.value,
                "interview_type": InterviewType.TECHNICAL.value,
                "status": InterviewStatus.COMPLETED.value,
                "focus_areas": ["FastAPI", "PostgreSQL", "System Design"],
                "duration_minutes": 60,
                "started_at": now - timedelta(days=1, minutes=55),
                "completed_at": now - timedelta(days=1),
                "overall_score": Decimal("86.50"),
                "is_archived": False,
            },
        )

        await upsert(
            session,
            Question,
            question_id,
            {
                "interview_id": interview_id,
                "category": QuestionCategory.SYSTEM_DESIGN.value,
                "difficulty": DifficultyLevel.HARD.value,
                "prompt": "Design a scalable interview practice platform that evaluates candidate answers.",
                "expected_signal": "architecture_tradeoffs",
                "rubric": {
                    "excellent": "Explains data model, queueing, observability, privacy, and scaling tradeoffs.",
                    "needs_work": "Focuses only on API routes without discussing reliability or data boundaries.",
                },
                "tags": ["system-design", "backend", "scalability"],
                "order_index": 1,
                "is_active": True,
            },
        )

        await upsert(
            session,
            Answer,
            answer_id,
            {
                "user_id": user_id,
                "interview_id": interview_id,
                "question_id": question_id,
                "transcript": "I would separate the web client, API, scoring workers, and persistent data stores...",
                "duration_seconds": 420,
                "score": Decimal("88.00"),
                "feedback": {
                    "strengths": ["Clear service boundaries", "Strong reliability discussion"],
                    "improvements": ["Add more detail about data retention"],
                },
            },
        )

        await upsert(
            session,
            Report,
            report_id,
            {
                "user_id": user_id,
                "interview_id": interview_id,
                "title": "Senior Backend Engineer Practice Report",
                "summary": "Strong backend architecture answer with clear decomposition and pragmatic scaling choices.",
                "status": ReportStatus.GENERATED.value,
                "overall_score": Decimal("86.50"),
                "strengths": ["API design", "System decomposition", "Operational awareness"],
                "improvement_areas": ["Privacy controls", "Data retention policy"],
                "recommendations": ["Practice privacy-by-design answers", "Prepare metrics and tracing examples"],
                "version": 1,
            },
        )

        await upsert(
            session,
            LearningRoadmap,
            roadmap_id,
            {
                "user_id": user_id,
                "report_id": report_id,
                "title": "Backend Interview Readiness Roadmap",
                "target_role": "Senior Backend Engineer",
                "status": RoadmapStatus.ACTIVE.value,
                "estimated_weeks": 4,
                "recommended_topics": ["Distributed tracing", "Data privacy", "PostgreSQL indexing"],
                "milestones": [
                    {"week": 1, "goal": "Review API observability patterns"},
                    {"week": 2, "goal": "Practice database scaling tradeoffs"},
                    {"week": 3, "goal": "Prepare privacy and retention answers"},
                    {"week": 4, "goal": "Run full mock interview"},
                ],
            },
        )

        await upsert(
            session,
            Leaderboard,
            leaderboard_id,
            {
                "user_id": user_id,
                "period": LeaderboardPeriod.WEEKLY.value,
                "rank": 1,
                "score": Decimal("965.00"),
                "percentile": Decimal("99.00"),
                "interviews_completed": 12,
            },
        )

        await upsert(
            session,
            Session,
            session_id,
            {
                "user_id": user_id,
                "token_jti": "seed-session-token-jti",
                "status": SessionStatus.ACTIVE.value,
                "ip_address": "127.0.0.1",
                "user_agent": "OfferPilot AI Seed Script",
                "expires_at": now + timedelta(days=7),
                "revoked_at": None,
            },
        )

        await upsert(
            session,
            RefreshToken,
            refresh_token_id,
            {
                "user_id": user_id,
                "session_id": session_id,
                "jti": "seed-refresh-token-jti",
                "token_hash": create_token_fingerprint("seed-refresh-token"),
                "expires_at": now + timedelta(days=7),
                "revoked_at": None,
                "replaced_by_jti": None,
                "ip_address": "127.0.0.1",
                "user_agent": "OfferPilot AI Seed Script",
            },
        )

        await upsert(
            session,
            CodeSubmission,
            code_submission_id,
            {
                "user_id": user_id,
                "interview_id": interview_id,
                "language": CodingLanguage.PYTHON.value,
                "prompt_title": "Two Sum Optimization",
                "prompt": "Return the indices of two numbers that add up to a target.",
                "source_code": (
                    "def two_sum(nums, target):\n"
                    "    for i in range(len(nums)):\n"
                    "        for j in range(i + 1, len(nums)):\n"
                    "            if nums[i] + nums[j] == target:\n"
                    "                return [i, j]\n"
                    "    return []\n"
                ),
                "stdin": "",
                "expected_output": "[0, 1]",
                "status": CodeRunStatus.SUCCESS.value,
                "stdout": "[0, 1]",
                "stderr": "",
                "exit_code": 0,
                "execution_time_ms": 12,
                "memory_kb": None,
                "time_complexity": "O(n^2)",
                "space_complexity": "O(1)",
                "bugs": [
                    {
                        "severity": "info",
                        "message": "range(len(...)) can usually be replaced with enumerate.",
                        "line": None,
                        "rule": "python.range_len",
                    }
                ],
                "optimized_code": (
                    "def two_sum(nums, target):\n"
                    "    seen = {}\n"
                    "    for index, value in enumerate(nums):\n"
                    "        complement = target - value\n"
                    "        if complement in seen:\n"
                    "            return [seen[complement], index]\n"
                    "        seen[value] = index\n"
                    "    return []\n"
                ),
                "improvement_explanation": "Use a hash map to reduce nested scans from O(n^2) to O(n).",
                "analysis": {
                    "quality_score": "79.00",
                    "analyzer_version": "heuristic-code-analyzer-v1",
                    "improvement_suggestions": ["Use a hash map to reduce nested scans."],
                },
                "metadata_json": {"source": "seed"},
                "submitted_at": now - timedelta(hours=8),
            },
        )

        await upsert(
            session,
            ResumeAnalysis,
            resume_analysis_id,
            {
                "user_id": user_id,
                "filename": "avery-candidate-resume.pdf",
                "content_type": "application/pdf",
                "file_size": 128000,
                "resume_text": (
                    "Avery Candidate Senior Backend Engineer. Summary: built FastAPI Python services, "
                    "PostgreSQL data models, Docker deployments, observability, and system design reviews. "
                    "Experience: led cross-functional projects, improved API latency by 35%, mentored engineers, "
                    "and launched interview analytics features. Skills: Python, SQL, FastAPI, Docker, AWS, "
                    "Testing, Observability, Leadership, Communication."
                ),
                "job_description": (
                    "Senior Backend Engineer role requiring Python, SQL, AWS, Kubernetes, system design, "
                    "observability, security, and CI/CD experience."
                ),
                "extracted_skills": [
                    {"name": "Python", "category": "Programming", "evidence_count": 2, "confidence": "82.00"},
                    {"name": "SQL", "category": "Data", "evidence_count": 2, "confidence": "82.00"},
                    {"name": "Docker", "category": "DevOps", "evidence_count": 1, "confidence": "70.00"},
                    {"name": "AWS", "category": "Cloud", "evidence_count": 1, "confidence": "70.00"},
                    {"name": "Observability", "category": "Operations", "evidence_count": 2, "confidence": "82.00"},
                ],
                "matched_skills": [
                    {"name": "Python", "category": "Programming", "evidence_count": 1, "confidence": "70.00"},
                    {"name": "SQL", "category": "Data", "evidence_count": 1, "confidence": "70.00"},
                    {"name": "AWS", "category": "Cloud", "evidence_count": 1, "confidence": "70.00"},
                    {"name": "Observability", "category": "Operations", "evidence_count": 1, "confidence": "70.00"},
                ],
                "missing_skills": [
                    {
                        "name": "Kubernetes",
                        "category": "DevOps",
                        "priority": "medium",
                        "reason": "The job description emphasizes Kubernetes, but the resume does not show a clear match.",
                    },
                    {
                        "name": "Security",
                        "category": "Security",
                        "priority": "medium",
                        "reason": "The job description emphasizes Security, but the resume does not show a clear match.",
                    },
                ],
                "ats_score": Decimal("84.50"),
                "resume_suggestions": [
                    "Add Kubernetes deployment evidence if applicable.",
                    "Add security and CI/CD keywords with concrete project context.",
                    "Quantify more backend reliability outcomes.",
                ],
                "interview_questions": [
                    {
                        "question": "Walk me through a project where you used Python. What tradeoffs did you make?",
                        "category": "Programming",
                        "difficulty": "medium",
                        "signal": "evidence_depth",
                    },
                    {
                        "question": "The role mentions Kubernetes. How would you ramp up and apply it in the first 30 days?",
                        "category": "DevOps",
                        "difficulty": "medium",
                        "signal": "skill_gap_reasoning",
                    },
                ],
                "skill_gap_report": {
                    "match_rate": "66.67",
                    "strongest_categories": ["Programming", "Data", "Operations"],
                    "weakest_categories": ["DevOps", "Security"],
                    "priority_gaps": [
                        {
                            "name": "Kubernetes",
                            "category": "DevOps",
                            "priority": "medium",
                            "reason": "The job description emphasizes Kubernetes, but the resume does not show a clear match.",
                        }
                    ],
                    "recommended_focus": ["Kubernetes", "Security"],
                    "summary": "Skill match rate is 66.67%. Address deployment and security gaps first.",
                },
                "analysis_summary": "ATS score is 84.50 with strong backend alignment and a few infrastructure gaps.",
                "analyzer_version": "heuristic-resume-analyzer-v1",
                "metadata_json": {"source": "seed"},
                "analyzed_at": now - timedelta(hours=4),
            },
        )

        await upsert(
            session,
            InterviewHistory,
            history_id,
            {
                "user_id": user_id,
                "interview_id": interview_id,
                "event_type": InterviewHistoryEvent.COMPLETED.value,
                "event_payload": {"source": "seed", "score": 86.5},
                "occurred_at": now - timedelta(days=1),
            },
        )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
