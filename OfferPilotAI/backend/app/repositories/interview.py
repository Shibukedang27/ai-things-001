"""Interview repository."""

from app.models import Interview
from app.repositories.base import SQLAlchemyRepository


class InterviewRepository(SQLAlchemyRepository[Interview]):
    model = Interview
