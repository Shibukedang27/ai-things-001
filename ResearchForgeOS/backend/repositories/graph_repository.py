from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from backend.models.interactive_graph import (
    GraphEdge,
    GraphLayout,
    GraphNode,
    GraphSnapshot,
    NodeMetadata,
    RelationshipMetadata,
)
from backend.repositories.base import BaseRepository


class GraphNodeRepository(BaseRepository[GraphNode]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, GraphNode)

    def get_by_stable_key(self, stable_key: str) -> GraphNode | None:
        statement = (
            select(GraphNode)
            .where(GraphNode.stable_key == stable_key)
            .options(selectinload(GraphNode.metadata_items))
        )
        return self.session.scalars(statement).first()

    def get_full(self, node_id: str) -> GraphNode | None:
        statement = select(GraphNode).where(GraphNode.id == node_id).options(selectinload(GraphNode.metadata_items))
        return self.session.scalars(statement).first()

    def list_nodes(
        self,
        *,
        offset: int = 0,
        limit: int = 500,
        node_type: str | None = None,
        query: str | None = None,
        include_collapsed: bool = True,
    ) -> Sequence[GraphNode]:
        statement = select(GraphNode).options(selectinload(GraphNode.metadata_items))
        if node_type:
            statement = statement.where(GraphNode.node_type == node_type)
        if query:
            pattern = f"%{query}%"
            statement = statement.where(or_(GraphNode.name.ilike(pattern), GraphNode.label.ilike(pattern)))
        if not include_collapsed:
            statement = statement.where(GraphNode.is_collapsed.is_(False))
        statement = (
            statement.order_by(GraphNode.importance_score.desc(), GraphNode.name.asc())
            .offset(offset)
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def search(self, query: str, *, limit: int = 25) -> Sequence[GraphNode]:
        pattern = f"%{query}%"
        statement = (
            select(GraphNode)
            .where(
                or_(
                    GraphNode.name.ilike(pattern),
                    GraphNode.label.ilike(pattern),
                    GraphNode.description.ilike(pattern),
                )
            )
            .options(selectinload(GraphNode.metadata_items))
            .order_by(GraphNode.importance_score.desc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def by_stable_keys(self, keys: set[str]) -> Sequence[GraphNode]:
        if not keys:
            return []
        statement = (
            select(GraphNode)
            .where(GraphNode.stable_key.in_(keys))
            .options(selectinload(GraphNode.metadata_items))
        )
        return self.session.scalars(statement).all()


class GraphEdgeRepository(BaseRepository[GraphEdge]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, GraphEdge)

    def get_by_stable_key(self, stable_key: str) -> GraphEdge | None:
        statement = (
            select(GraphEdge)
            .where(GraphEdge.stable_key == stable_key)
            .options(selectinload(GraphEdge.metadata_items))
        )
        return self.session.scalars(statement).first()

    def list_edges(
        self,
        *,
        node_ids: set[str] | None = None,
        offset: int = 0,
        limit: int = 1500,
    ) -> Sequence[GraphEdge]:
        statement = select(GraphEdge).options(
            selectinload(GraphEdge.source_node),
            selectinload(GraphEdge.target_node),
            selectinload(GraphEdge.metadata_items),
        )
        if node_ids:
            statement = statement.where(
                or_(GraphEdge.source_node_id.in_(node_ids), GraphEdge.target_node_id.in_(node_ids))
            )
        statement = statement.order_by(GraphEdge.weight.desc()).offset(offset).limit(limit)
        return self.session.scalars(statement).all()

    def neighbors(self, node_id: str, *, limit: int = 100) -> Sequence[GraphEdge]:
        statement = (
            select(GraphEdge)
            .where(or_(GraphEdge.source_node_id == node_id, GraphEdge.target_node_id == node_id))
            .options(
                selectinload(GraphEdge.source_node),
                selectinload(GraphEdge.target_node),
                selectinload(GraphEdge.metadata_items),
            )
            .order_by(GraphEdge.weight.desc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def get_full(self, edge_id: str) -> GraphEdge | None:
        statement = (
            select(GraphEdge)
            .where(GraphEdge.id == edge_id)
            .options(
                selectinload(GraphEdge.source_node),
                selectinload(GraphEdge.target_node),
                selectinload(GraphEdge.metadata_items),
            )
        )
        return self.session.scalars(statement).first()


class NodeMetadataRepository(BaseRepository[NodeMetadata]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, NodeMetadata)


class RelationshipMetadataRepository(BaseRepository[RelationshipMetadata]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, RelationshipMetadata)


class GraphLayoutRepository(BaseRepository[GraphLayout]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, GraphLayout)

    def default(self) -> GraphLayout | None:
        statement = select(GraphLayout).where(GraphLayout.is_default.is_(True)).order_by(GraphLayout.updated_at.desc())
        return self.session.scalars(statement).first()


class GraphSnapshotRepository(BaseRepository[GraphSnapshot]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, GraphSnapshot)

    def latest(self) -> GraphSnapshot | None:
        statement = select(GraphSnapshot).order_by(GraphSnapshot.created_at.desc()).limit(1)
        return self.session.scalars(statement).first()

    def list_snapshots(self, *, offset: int = 0, limit: int = 50) -> Sequence[GraphSnapshot]:
        statement = select(GraphSnapshot).order_by(GraphSnapshot.created_at.desc()).offset(offset).limit(limit)
        return self.session.scalars(statement).all()


__all__ = [
    "GraphEdge",
    "GraphEdgeRepository",
    "GraphLayout",
    "GraphLayoutRepository",
    "GraphNode",
    "GraphNodeRepository",
    "GraphSnapshot",
    "GraphSnapshotRepository",
    "NodeMetadata",
    "NodeMetadataRepository",
    "RelationshipMetadata",
    "RelationshipMetadataRepository",
]
