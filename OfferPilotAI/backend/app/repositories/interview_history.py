"""Interview history repository."""

from app.models import InterviewHistory
from app.repositories.base import SQLAlchemyRepository


class InterviewHistoryRepository(SQLAlchemyRepository[InterviewHistory]):
    model = InterviewHistory
