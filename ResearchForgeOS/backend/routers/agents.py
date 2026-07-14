from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_permissions
from backend.dependencies.database import get_db
from backend.models.agent import Agent, PipelineHistory
from backend.models.user import User
from backend.schemas.agent import (
    AgentStatusRead,
    MultiAgentAnalysisRequest,
    PipelineHistoryRead,
    PipelineStatusRead,
    TaskActionResponse,
)
from backend.services.agent_service import AgentService

router = APIRouter()


@router.post(
    "/analyze",
    response_model=PipelineHistoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Run Multi-Agent Analysis",
)
async def run_multi_agent_analysis(
    payload: MultiAgentAnalysisRequest,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("agents:write"))],
) -> PipelineHistory:
    return await AgentService(session).run_analysis(payload, current_user)


@router.get("/status", response_model=list[AgentStatusRead], summary="Get Agent Status")
def get_agent_status(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("agents:read"))],
) -> list[Agent]:
    return AgentService(session).list_agent_status()


@router.get("/history", response_model=list[PipelineHistoryRead], summary="Execution History")
def get_execution_history(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("agents:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[PipelineHistory]:
    return AgentService(session).execution_history(offset=offset, limit=limit)


@router.get(
    "/pipelines/{pipeline_id}/status",
    response_model=PipelineStatusRead,
    summary="Pipeline Status",
)
def get_pipeline_status(
    pipeline_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("agents:read"))],
) -> PipelineStatusRead:
    return AgentService(session).pipeline_status(pipeline_id)


@router.post("/tasks/{task_id}/cancel", response_model=TaskActionResponse, summary="Cancel Task")
def cancel_task(
    task_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("agents:write"))],
) -> TaskActionResponse:
    return AgentService(session).cancel_task(task_id)


@router.post("/tasks/{task_id}/retry", response_model=TaskActionResponse, summary="Retry Task")
async def retry_task(
    task_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("agents:write"))],
) -> TaskActionResponse:
    return await AgentService(session).retry_task(task_id)
