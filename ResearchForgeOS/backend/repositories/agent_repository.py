from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.agent import Agent, AgentResponse, AgentTask, ExecutionLog, PipelineHistory
from backend.repositories.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Agent)

    def get_by_role(self, role: str) -> Agent | None:
        return self.session.scalars(select(Agent).where(Agent.role == role)).first()

    def list_agents(self) -> Sequence[Agent]:
        return self.session.scalars(select(Agent).order_by(Agent.default_priority.asc())).all()


class PipelineHistoryRepository(BaseRepository[PipelineHistory]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, PipelineHistory)

    def get_full(self, pipeline_id: str) -> PipelineHistory | None:
        statement = select(PipelineHistory).where(PipelineHistory.id == pipeline_id).options(*self._load_options())
        return self.session.scalars(statement).first()

    def list_history(self, *, offset: int = 0, limit: int = 50) -> Sequence[PipelineHistory]:
        statement = (
            select(PipelineHistory)
            .options(*self._load_options())
            .order_by(PipelineHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def _load_options(self) -> tuple[object, ...]:
        return (
            selectinload(PipelineHistory.tasks).selectinload(AgentTask.responses),
            selectinload(PipelineHistory.logs),
        )


class AgentTaskRepository(BaseRepository[AgentTask]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AgentTask)

    def get_full(self, task_id: str) -> AgentTask | None:
        statement = select(AgentTask).where(AgentTask.id == task_id).options(selectinload(AgentTask.responses))
        return self.session.scalars(statement).first()

    def list_by_pipeline(self, pipeline_id: str) -> Sequence[AgentTask]:
        statement = (
            select(AgentTask)
            .where(AgentTask.pipeline_id == pipeline_id)
            .options(selectinload(AgentTask.responses))
            .order_by(AgentTask.priority.asc())
        )
        return self.session.scalars(statement).all()


__all__ = [
    "Agent",
    "AgentRepository",
    "AgentResponse",
    "AgentTask",
    "AgentTaskRepository",
    "ExecutionLog",
    "PipelineHistory",
    "PipelineHistoryRepository",
]
