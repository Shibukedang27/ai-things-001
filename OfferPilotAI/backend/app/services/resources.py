"""Concrete resource CRUD services."""

from app.models import Answer, Interview, InterviewHistory, Leaderboard, LearningRoadmap, Question, Report, Session, User
from app.repositories import (
    AnswerRepository,
    InterviewHistoryRepository,
    InterviewRepository,
    LeaderboardRepository,
    LearningRoadmapRepository,
    QuestionRepository,
    ReportRepository,
    SessionRepository,
    UserRepository,
)
from app.services.crud import CRUDService


class UserCRUDService(CRUDService[User, UserRepository]):
    repository_cls = UserRepository
    resource_name = "user"


class InterviewCRUDService(CRUDService[Interview, InterviewRepository]):
    repository_cls = InterviewRepository
    resource_name = "interview"

    def prepare_create_values(self, values: dict) -> dict:
        if not values.get("title"):
            values["title"] = values["role_title"]
        return values


class QuestionCRUDService(CRUDService[Question, QuestionRepository]):
    repository_cls = QuestionRepository
    resource_name = "question"


class AnswerCRUDService(CRUDService[Answer, AnswerRepository]):
    repository_cls = AnswerRepository
    resource_name = "answer"


class ReportCRUDService(CRUDService[Report, ReportRepository]):
    repository_cls = ReportRepository
    resource_name = "report"


class LearningRoadmapCRUDService(CRUDService[LearningRoadmap, LearningRoadmapRepository]):
    repository_cls = LearningRoadmapRepository
    resource_name = "learning roadmap"


class LeaderboardCRUDService(CRUDService[Leaderboard, LeaderboardRepository]):
    repository_cls = LeaderboardRepository
    resource_name = "leaderboard entry"


class SessionCRUDService(CRUDService[Session, SessionRepository]):
    repository_cls = SessionRepository
    resource_name = "session"


class InterviewHistoryCRUDService(CRUDService[InterviewHistory, InterviewHistoryRepository]):
    repository_cls = InterviewHistoryRepository
    resource_name = "interview history"
