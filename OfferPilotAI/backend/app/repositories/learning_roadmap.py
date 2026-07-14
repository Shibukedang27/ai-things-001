"""Learning roadmap repository."""

from app.models import LearningRoadmap
from app.repositories.base import SQLAlchemyRepository


class LearningRoadmapRepository(SQLAlchemyRepository[LearningRoadmap]):
    model = LearningRoadmap
