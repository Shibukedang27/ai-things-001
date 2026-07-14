"""Question repository."""

from app.models import Question
from app.repositories.base import SQLAlchemyRepository


class QuestionRepository(SQLAlchemyRepository[Question]):
    model = Question
