"""Answer repository."""

from app.models import Answer
from app.repositories.base import SQLAlchemyRepository


class AnswerRepository(SQLAlchemyRepository[Answer]):
    model = Answer
