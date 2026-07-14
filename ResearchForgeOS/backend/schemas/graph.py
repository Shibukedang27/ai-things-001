from typing import Any, Literal

from pydantic import Field

from backend.schemas.common import APIModel, TimestampedRead


class NodeMetadataRead(TimestampedRead):
    id: str
    metadata_key: str
    metadata_value: str
    value_type: str
    confidence_score: float


class RelationshipMetadataRead(TimestampedRead):
    id: str
    metadata_key: str
    metadata_value: str
    value_type: str
    confidence_score: float


class GraphNodeRead(TimestampedRead):
    id: str
    stable_key: str
    node_type: str
    name: str
    label: str
    description: str
    document_id: str | None
    importance_score: float
    confidence_score: float
    degree: int
    cluster_id: str | None
    is_collapsed: bool
    position_x: float
    position_y: float
    size: float
    color: str
    metadata_json: dict[str, Any]
    metadata_items: list[NodeMetadataRead] = Field(default_factory=list)


class GraphEdgeRead(TimestampedRead):
    id: str
    stable_key: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    label: str
    description: str
    weight: float
    confidence_score: float
    is_bidirectional: bool
    metadata_json: dict[str, Any]
    metadata_items: list[RelationshipMetadataRead] = Field(default_factory=list)


class GraphLayoutRead(TimestampedRead):
    id: str
    layout_name: str
    algorithm: str
    is_default: bool
    viewport: dict[str, Any]
    positions: list[dict[str, Any]]
    settings: dict[str, Any]


class GraphAnalyticsRead(APIModel):
    node_count: int
    edge_count: int
    cluster_count: int
    graph_density: float
    knowledge_score: float
    coverage_score: float
    mastery_score: float
    learning_progress: float
    average_degree: float


class GraphRead(APIModel):
    nodes: list[GraphNodeRead]
    edges: list[GraphEdgeRead]
    layout: GraphLayoutRead | None
    analytics: GraphAnalyticsRead
    insights: dict[str, Any]
    interaction: dict[str, Any]
    total_nodes: int
    total_edges: int
    cache_hit: bool = False


class GraphNodeUpdate(APIModel):
    label: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, min_length=1)
    importance_score: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    is_collapsed: bool | None = None
    position_x: float | None = None
    position_y: float | None = None
    metadata_json: dict[str, Any] | None = None


class GraphSearchResponse(APIModel):
    query: str
    results: list[GraphNodeRead]


class GraphExpansionResponse(APIModel):
    center_node: GraphNodeRead
    nodes: list[GraphNodeRead]
    edges: list[GraphEdgeRead]
    depth: int


class GraphCollapseResponse(APIModel):
    node_id: str
    collapsed: bool
    hidden_neighbor_count: int


class GraphSnapshotCreate(APIModel):
    name: str = Field(default="Knowledge Graph Snapshot", min_length=1, max_length=160)
    snapshot_type: str = Field(default="manual", min_length=1, max_length=80)


class GraphSnapshotRead(TimestampedRead):
    id: str
    name: str
    snapshot_type: str
    node_count: int
    edge_count: int
    analytics: dict[str, Any]
    insights: dict[str, Any]
    graph_payload: dict[str, Any]
    generated_by_user_id: str | None


class GraphExportQuery(APIModel):
    format: Literal["json", "svg", "png"] = "json"
