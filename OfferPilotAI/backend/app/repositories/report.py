"""Report repository."""

from app.models import Report
from app.repositories.base import SQLAlchemyRepository


class ReportRepository(SQLAlchemyRepository[Report]):
    model = Report
