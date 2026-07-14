"""Versioned API router."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_principal
from app.api.v1.endpoints import (
    analytics,
    answers,
    auth,
    evaluations,
    health,
    interview_engine,
    interview_history,
    interviews,
    leaderboard,
    learning_roadmaps,
    live_coding,
    questions,
    recommendations,
    reports,
    resume_analyzer,
    sessions,
    users,
)

router = APIRouter()
protected_route = [Depends(get_current_principal)]

router.include_router(health.router, tags=["Health"])
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(interview_engine.router, prefix="/interview-engine", tags=["Interview Engine"])
router.include_router(evaluations.router, prefix="/evaluations", tags=["AI Evaluation"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["Learning Recommendations"])
router.include_router(live_coding.router, prefix="/live-coding", tags=["Live Coding"])
router.include_router(resume_analyzer.router, prefix="/resume-analyzer", tags=["Resume Analyzer"])
router.include_router(users.router, prefix="/users", tags=["Users"], dependencies=protected_route)
router.include_router(questions.router, prefix="/questions", tags=["Question Catalog"])
router.include_router(interviews.router, prefix="/interviews", tags=["Interview Sessions"])
router.include_router(answers.router, prefix="/answers", tags=["Answers"], dependencies=protected_route)
router.include_router(reports.router, prefix="/reports", tags=["Reports"], dependencies=protected_route)
router.include_router(
    learning_roadmaps.router,
    prefix="/learning-roadmaps",
    tags=["Learning Roadmaps"],
    dependencies=protected_route,
)
router.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"], dependencies=protected_route)
router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"], dependencies=protected_route)
router.include_router(
    interview_history.router,
    prefix="/interview-history",
    tags=["Interview History"],
    dependencies=protected_route,
)
