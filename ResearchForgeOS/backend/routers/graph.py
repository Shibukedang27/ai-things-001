from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from backend.dependencies.auth import require_permissions
from backend.dependencies.database import get_db
from backend.models.interactive_graph import GraphNode, GraphSnapshot
from backend.models.user import User
from backend.schemas.common import MessageResponse
from backend.schemas.graph import (
    GraphCollapseResponse,
    GraphExpansionResponse,
    GraphNodeRead,
    GraphNodeUpdate,
    GraphRead,
    GraphSearchResponse,
    GraphSnapshotCreate,
    GraphSnapshotRead,
)
from backend.services.graph_service import InteractiveKnowledgeGraphService

router = APIRouter()


@router.get("", response_model=GraphRead, summary="Get Graph")
def get_graph(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=5000),
    node_type: str | None = Query(default=None, max_length=80),
    query: str | None = Query(default=None, max_length=240),
    include_collapsed: bool = True,
) -> GraphRead:
    return InteractiveKnowledgeGraphService(session).get_graph(
        offset=offset,
        limit=limit,
        node_type=node_type,
        query=query,
        include_collapsed=include_collapsed,
    )


@router.post(
    "/documents/{document_id}/generate",
    response_model=GraphRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Graph For Document",
)
def generate_graph_for_document(
    document_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:write"))],
) -> GraphRead:
    return InteractiveKnowledgeGraphService(session).generate_for_document(document_id)


@router.get("/nodes/search", response_model=GraphSearchResponse, summary="Search Nodes")
def search_nodes(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:read"))],
    query: str = Query(min_length=1, max_length=240),
    limit: int = Query(default=25, ge=1, le=100),
) -> GraphSearchResponse:
    return InteractiveKnowledgeGraphService(session).search_nodes(query, limit=limit)


@router.get("/nodes/{node_id}", response_model=GraphNodeRead, summary="Get Node")
def get_node(
    node_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:read"))],
) -> GraphNode:
    return InteractiveKnowledgeGraphService(session).get_node(node_id)


@router.patch("/nodes/{node_id}", response_model=GraphNodeRead, summary="Update Node")
def update_node(
    node_id: str,
    payload: GraphNodeUpdate,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:write"))],
) -> GraphNode:
    return InteractiveKnowledgeGraphService(session).update_node(node_id, payload)


@router.delete("/nodes/{node_id}", response_model=MessageResponse, summary="Delete Node")
def delete_node(
    node_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:write"))],
) -> MessageResponse:
    InteractiveKnowledgeGraphService(session).delete_node(node_id)
    return MessageResponse(message="Graph node deleted.")


@router.get("/nodes/{node_id}/expand", response_model=GraphExpansionResponse, summary="Expand Node")
def expand_node(
    node_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:read"))],
    depth: int = Query(default=1, ge=1, le=4),
    limit: int = Query(default=120, ge=1, le=1000),
) -> GraphExpansionResponse:
    return InteractiveKnowledgeGraphService(session).expand_node(node_id, depth=depth, limit=limit)


@router.post("/nodes/{node_id}/collapse", response_model=GraphCollapseResponse, summary="Collapse Node")
def collapse_node(
    node_id: str,
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:write"))],
) -> GraphCollapseResponse:
    return InteractiveKnowledgeGraphService(session).collapse_node(node_id)


@router.get("/export", summary="Export Graph")
def export_graph(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:read"))],
    format: str = Query(default="json", pattern="^(json|svg|png)$"),
) -> Response:
    payload, media_type = InteractiveKnowledgeGraphService(session).export_graph(format)
    return Response(content=payload, media_type=media_type)


@router.post(
    "/snapshots",
    response_model=GraphSnapshotRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Graph Snapshot",
)
def generate_graph_snapshot(
    payload: GraphSnapshotCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permissions("graph:write"))],
) -> GraphSnapshot:
    return InteractiveKnowledgeGraphService(session).generate_snapshot(payload, current_user)


@router.get("/snapshots", response_model=list[GraphSnapshotRead], summary="List Graph Snapshots")
def list_graph_snapshots(
    session: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("graph:read"))],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[GraphSnapshotRead]:
    return InteractiveKnowledgeGraphService(session).list_snapshots(offset=offset, limit=limit)
