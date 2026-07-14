from __future__ import annotations

import json
import logging
from typing import Any

import networkx as nx
from graph_engine import GraphBuildInput, GraphBuildResult, GraphEdgeDraft, GraphNodeDraft
from graph_engine.analytics import GraphAnalyticsEngine
from graph_engine.cache import GraphCache
from graph_engine.engine import InteractiveKnowledgeGraphEngine
from graph_engine.exporter import GraphExporter
from graph_engine.layout import InteractionManager, LayoutManager
from graph_engine.types import (
    GraphConceptInput,
    GraphDNAInput,
    GraphDocumentInput,
    GraphReferenceInput,
    GraphRelationshipInput,
    GraphTechnologyInput,
)
from graph_engine.utils import merge_metadata
from sqlalchemy.orm import Session

from backend.exceptions import NotFoundError, ValidationError
from backend.models.document import Document
from backend.models.interactive_graph import (
    GraphEdge,
    GraphLayout,
    GraphNode,
    GraphSnapshot,
    NodeMetadata,
    RelationshipMetadata,
)
from backend.models.knowledge_dna import KnowledgeDNA
from backend.models.user import User
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.graph_repository import (
    GraphEdgeRepository,
    GraphLayoutRepository,
    GraphNodeRepository,
    GraphSnapshotRepository,
)
from backend.repositories.knowledge_dna_repository import KnowledgeDNARepository
from backend.schemas.graph import (
    GraphAnalyticsRead,
    GraphCollapseResponse,
    GraphExpansionResponse,
    GraphNodeUpdate,
    GraphRead,
    GraphSearchResponse,
    GraphSnapshotCreate,
    GraphSnapshotRead,
)

logger = logging.getLogger(__name__)
GRAPH_CACHE = GraphCache(ttl_seconds=120)


class InteractiveKnowledgeGraphService:
    def __init__(
        self,
        session: Session,
        engine: InteractiveKnowledgeGraphEngine | None = None,
        exporter: GraphExporter | None = None,
    ) -> None:
        self.session = session
        self.engine = engine or InteractiveKnowledgeGraphEngine()
        self.exporter = exporter or GraphExporter()
        self.documents = DocumentRepository(session)
        self.dna = KnowledgeDNARepository(session)
        self.nodes = GraphNodeRepository(session)
        self.edges = GraphEdgeRepository(session)
        self.layouts = GraphLayoutRepository(session)
        self.snapshots = GraphSnapshotRepository(session)
        self.analytics_engine = GraphAnalyticsEngine()
        self.layout_manager = LayoutManager()
        self.interaction_manager = InteractionManager()

    def sync_document_graph(self, document: Document) -> GraphBuildResult:
        dna = self.dna.get_by_document_id(document.id)
        result = self.engine.build(GraphBuildInput(document=self._document_input(document, dna)))
        node_lookup = self._upsert_nodes(result.nodes, document_id=document.id)
        self._upsert_edges(result.edges, node_lookup)
        self._refresh_global_layout()
        GRAPH_CACHE.invalidate()
        logger.info("Interactive graph synced", extra={"document_id": document.id, "nodes": len(result.nodes)})
        return result

    def generate_for_document(self, document_id: str) -> GraphRead:
        document = self._document(document_id)
        self.sync_document_graph(document)
        self.session.commit()
        return self.get_graph()

    def refresh_layout(self) -> None:
        self._refresh_global_layout()
        GRAPH_CACHE.invalidate()

    def delete_document_graph(self, document_id: str) -> None:
        all_edges = list(self.edges.list_edges(limit=100_000))
        for edge in all_edges:
            source_ids = self._source_ids(edge.metadata_json)
            if document_id not in source_ids:
                continue
            remaining = [source_id for source_id in source_ids if source_id != document_id]
            if remaining:
                edge.metadata_json = {**edge.metadata_json, "source_document_ids": remaining}
            else:
                self.session.delete(edge)

        all_nodes = list(self.nodes.list_nodes(limit=100_000))
        for node in all_nodes:
            source_ids = self._source_ids(node.metadata_json)
            should_delete_document_node = node.document_id == document_id
            if document_id not in source_ids and not should_delete_document_node:
                continue
            remaining = [source_id for source_id in source_ids if source_id != document_id]
            if remaining and not should_delete_document_node:
                node.metadata_json = {**node.metadata_json, "source_document_ids": remaining}
            else:
                for edge in self.edges.neighbors(node.id, limit=100_000):
                    self.session.delete(edge)
                self.session.delete(node)
        self.session.flush()
        self._refresh_global_layout()
        GRAPH_CACHE.invalidate()

    def get_graph(
        self,
        *,
        offset: int = 0,
        limit: int = 500,
        node_type: str | None = None,
        query: str | None = None,
        include_collapsed: bool = True,
    ) -> GraphRead:
        cache_key = f"graph:{offset}:{limit}:{node_type}:{query}:{include_collapsed}"
        cached = GRAPH_CACHE.get(cache_key)
        if cached is not None:
            cached["cache_hit"] = True
            return GraphRead(**cached)

        nodes = list(
            self.nodes.list_nodes(
                offset=offset,
                limit=limit,
                node_type=node_type,
                query=query,
                include_collapsed=include_collapsed,
            )
        )
        node_ids = {node.id for node in nodes}
        edges = list(self.edges.list_edges(node_ids=node_ids, limit=limit * 3 if limit else 1500))
        analytics = self._current_analytics()
        layout = self.layouts.default()
        graph = GraphRead(
            nodes=nodes,
            edges=edges,
            layout=layout,
            analytics=GraphAnalyticsRead(**analytics["analytics"]),
            insights=analytics["insights"],
            interaction=self.interaction_manager.interaction_payload(
                analytics["total_nodes"],
                analytics["total_edges"],
            ),
            total_nodes=analytics["total_nodes"],
            total_edges=analytics["total_edges"],
            cache_hit=False,
        )
        GRAPH_CACHE.set(cache_key, graph.model_dump())
        return graph

    def get_node(self, node_id: str) -> GraphNode:
        node = self.nodes.get_full(node_id)
        if node is None:
            raise NotFoundError("Graph node was not found.")
        return node

    def update_node(self, node_id: str, payload: GraphNodeUpdate) -> GraphNode:
        node = self.get_node(node_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            if value is not None:
                setattr(node, field_name, value)
        self._sync_node_metadata(node)
        self.session.commit()
        GRAPH_CACHE.invalidate()
        return self.get_node(node_id)

    def delete_node(self, node_id: str) -> None:
        node = self.get_node(node_id)
        for edge in self.edges.neighbors(node.id, limit=100_000):
            self.session.delete(edge)
        self.session.delete(node)
        self.session.commit()
        self._refresh_global_layout()
        self.session.commit()
        GRAPH_CACHE.invalidate()

    def search_nodes(self, query: str, *, limit: int = 25) -> GraphSearchResponse:
        if not query.strip():
            raise ValidationError("Search query must not be empty.")
        return GraphSearchResponse(query=query, results=list(self.nodes.search(query, limit=limit)))

    def expand_node(self, node_id: str, *, depth: int = 1, limit: int = 120) -> GraphExpansionResponse:
        center = self.get_node(node_id)
        visited = {center.id}
        frontier = {center.id}
        collected_edges: dict[str, GraphEdge] = {}
        for _level in range(depth):
            next_frontier: set[str] = set()
            for current_id in frontier:
                for edge in self.edges.neighbors(current_id, limit=limit):
                    collected_edges[edge.id] = edge
                    neighbor_id = edge.target_node_id if edge.source_node_id == current_id else edge.source_node_id
                    if neighbor_id not in visited:
                        next_frontier.add(neighbor_id)
                        visited.add(neighbor_id)
                    if len(visited) >= limit:
                        break
                if len(visited) >= limit:
                    break
            frontier = next_frontier
            if not frontier:
                break
        expanded_nodes = [node for node in self.nodes.list_nodes(limit=100_000) if node.id in visited]
        return GraphExpansionResponse(
            center_node=center,
            nodes=expanded_nodes,
            edges=list(collected_edges.values()),
            depth=depth,
        )

    def collapse_node(self, node_id: str) -> GraphCollapseResponse:
        node = self.get_node(node_id)
        neighbor_count = len(self.edges.neighbors(node.id, limit=100_000))
        node.is_collapsed = True
        self.session.commit()
        GRAPH_CACHE.invalidate()
        return GraphCollapseResponse(node_id=node.id, collapsed=True, hidden_neighbor_count=neighbor_count)

    def export_graph(self, export_format: str) -> tuple[str | bytes, str]:
        payload = self._graph_payload(self.get_graph(limit=10_000))
        if export_format == "json":
            return self.exporter.export_json(payload), "application/json"
        if export_format == "svg":
            return self.exporter.export_svg(payload), "image/svg+xml"
        if export_format == "png":
            return self.exporter.export_png(payload), "image/png"
        raise ValidationError("Unsupported export format.", details={"valid_formats": ["json", "svg", "png"]})

    def generate_snapshot(self, payload: GraphSnapshotCreate, current_user: User) -> GraphSnapshot:
        graph = self.get_graph(limit=10_000)
        graph_payload = self._graph_payload(graph)
        snapshot = GraphSnapshot(
            name=payload.name,
            snapshot_type=payload.snapshot_type,
            node_count=graph.total_nodes,
            edge_count=graph.total_edges,
            analytics=graph.analytics.model_dump(),
            insights=graph.insights,
            graph_payload=graph_payload,
            generated_by_user_id=current_user.id,
        )
        self.snapshots.add(snapshot)
        self.session.commit()
        return snapshot

    def list_snapshots(self, *, offset: int = 0, limit: int = 50) -> list[GraphSnapshotRead]:
        return [
            GraphSnapshotRead.model_validate(snapshot)
            for snapshot in self.snapshots.list_snapshots(offset=offset, limit=limit)
        ]

    def _upsert_nodes(self, drafts: list[GraphNodeDraft], *, document_id: str) -> dict[str, GraphNode]:
        node_lookup: dict[str, GraphNode] = {}
        for draft in drafts:
            node = self.nodes.get_by_stable_key(draft.stable_key)
            document_fk = document_id if draft.node_type == "document" else None
            if node is None:
                node = GraphNode(
                    stable_key=draft.stable_key,
                    node_type=draft.node_type,
                    name=draft.name,
                    label=draft.label,
                    description=draft.description,
                    document_id=document_fk,
                    importance_score=draft.importance_score,
                    confidence_score=draft.confidence_score,
                    degree=0,
                    cluster_id=None,
                    is_collapsed=False,
                    position_x=0.0,
                    position_y=0.0,
                    size=draft.size,
                    color=draft.color,
                    metadata_json=draft.metadata,
                )
                self.nodes.add(node)
            else:
                node.label = draft.label
                node.description = (
                    draft.description
                    if len(draft.description) >= len(node.description)
                    else node.description
                )
                node.document_id = node.document_id or document_fk
                node.importance_score = max(node.importance_score, draft.importance_score)
                node.confidence_score = max(node.confidence_score, draft.confidence_score)
                node.size = max(node.size, draft.size)
                node.color = draft.color
                node.metadata_json = merge_metadata(node.metadata_json, draft.metadata)
            self._sync_node_metadata(node)
            node_lookup[draft.stable_key] = node
        self.session.flush()
        return node_lookup

    def _upsert_edges(self, drafts: list[GraphEdgeDraft], node_lookup: dict[str, GraphNode]) -> None:
        for draft in drafts:
            source = node_lookup.get(draft.source_key) or self.nodes.get_by_stable_key(draft.source_key)
            target = node_lookup.get(draft.target_key) or self.nodes.get_by_stable_key(draft.target_key)
            if source is None or target is None or source.id == target.id:
                continue
            edge = self.edges.get_by_stable_key(draft.stable_key)
            if edge is None:
                edge = GraphEdge(
                    stable_key=draft.stable_key,
                    source_node_id=source.id,
                    target_node_id=target.id,
                    relationship_type=draft.relationship_type,
                    label=draft.label,
                    description=draft.description,
                    weight=draft.weight,
                    confidence_score=draft.confidence_score,
                    is_bidirectional=False,
                    metadata_json=draft.metadata,
                )
                self.edges.add(edge)
            else:
                edge.weight = max(edge.weight, draft.weight)
                edge.confidence_score = max(edge.confidence_score, draft.confidence_score)
                edge.description = (
                    draft.description
                    if len(draft.description) >= len(edge.description)
                    else edge.description
                )
                edge.metadata_json = merge_metadata(edge.metadata_json, draft.metadata)
            self._sync_edge_metadata(edge)
        self.session.flush()

    def _refresh_global_layout(self) -> None:
        nodes = list(self.nodes.list_nodes(limit=100_000))
        edges = list(self.edges.list_edges(limit=200_000))
        node_drafts = [self._node_draft(node) for node in nodes]
        edge_drafts = [self._edge_draft(edge) for edge in edges if edge.source_node and edge.target_node]
        layout = self.layout_manager.layout(node_drafts, edge_drafts)
        position_lookup = {item.stable_key: item for item in layout}
        graph = nx.Graph()
        for node in nodes:
            graph.add_node(node.id)
        for edge in edges:
            graph.add_edge(edge.source_node_id, edge.target_node_id)
        cluster_lookup: dict[str, str] = {}
        for index, component in enumerate(nx.connected_components(graph)):
            for node_id in component:
                cluster_lookup[node_id] = f"cluster-{index + 1}"
        degree_lookup = dict(graph.degree())
        for node in nodes:
            position = position_lookup.get(node.stable_key)
            if position:
                node.position_x = position.x
                node.position_y = position.y
            node.degree = int(degree_lookup.get(node.id, 0))
            node.cluster_id = cluster_lookup.get(node.id)

        layout_model = self.layouts.default()
        positions = [
            {"node_id": node.id, "stable_key": node.stable_key, "x": node.position_x, "y": node.position_y}
            for node in nodes
        ]
        if layout_model is None:
            self.layouts.add(
                GraphLayout(
                    layout_name="Default Knowledge Graph Layout",
                    algorithm="networkx_spring_layout",
                    is_default=True,
                    viewport={"x": 0, "y": 0, "zoom": 1},
                    positions=positions,
                    settings={"supports_drag": True, "supports_auto_layout": True},
                )
            )
        else:
            layout_model.positions = positions
            layout_model.settings = {"supports_drag": True, "supports_auto_layout": True}
        self.session.flush()

    def _current_analytics(self) -> dict[str, Any]:
        nodes = list(self.nodes.list_nodes(limit=100_000))
        edges = list(self.edges.list_edges(limit=200_000))
        node_drafts = [self._node_draft(node) for node in nodes]
        edge_drafts = [self._edge_draft(edge) for edge in edges if edge.source_node and edge.target_node]
        return {
            "analytics": self.analytics_engine.analyze(node_drafts, edge_drafts),
            "insights": self.analytics_engine.insights(node_drafts, edge_drafts),
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }

    def _document_input(self, document: Document, dna: KnowledgeDNA | None) -> GraphDocumentInput:
        return GraphDocumentInput(
            id=document.id,
            title=document.title,
            author=document.author,
            category=document.category,
            source_type=document.source_type,
            difficulty=document.difficulty,
            created_at=document.created_at.isoformat() if document.created_at else None,
            topics=document.topics,
            keywords=[keyword.value for keyword in document.keywords],
            technologies=[
                GraphTechnologyInput(
                    id=technology.id,
                    name=technology.name,
                    category=technology.category,
                    confidence_score=technology.confidence_score,
                    evidence=technology.evidence,
                )
                for technology in document.technologies
            ],
            concepts=[
                GraphConceptInput(
                    id=concept.id,
                    name=concept.name,
                    concept_type=concept.concept_type,
                    description=concept.description,
                    prerequisites=concept.prerequisites,
                    dependencies=concept.dependencies,
                    difficulty_level=concept.difficulty_level,
                    confidence_score=concept.confidence_score,
                )
                for concept in document.concepts
            ],
            algorithms=[algorithm.get("name", "") for algorithm in document.algorithms if algorithm.get("name")],
            references=[
                GraphReferenceInput(
                    title=reference.title,
                    authors=reference.authors,
                    year=reference.year,
                    source=reference.source,
                    url=reference.url,
                    citation_text=reference.citation_text,
                    reference_type=reference.reference_type,
                    confidence_score=reference.confidence_score,
                )
                for reference in document.references
            ],
            relationships=[
                GraphRelationshipInput(
                    source_name=relationship.source_name,
                    target_name=relationship.target_name,
                    relationship_type=relationship.relationship_type,
                    description=relationship.description,
                    confidence_score=relationship.confidence_score,
                )
                for relationship in document.relationships
            ],
            cleaned_text=document.cleaned_text,
            dna=self._dna_input(dna),
        )

    def _dna_input(self, dna: KnowledgeDNA | None) -> GraphDNAInput | None:
        if dna is None:
            return None
        return GraphDNAInput(
            research_category=dna.research_category,
            knowledge_score=dna.knowledge_score,
            primary_concepts=dna.primary_concepts,
            secondary_concepts=dna.secondary_concepts,
            prerequisites=dna.prerequisites,
            advanced_topics=dna.advanced_topics,
            future_learning_topics=dna.future_learning_topics,
            technologies_used=dna.technologies_used,
            programming_languages=dna.programming_languages,
            frameworks=dna.frameworks,
            libraries=dna.libraries,
            algorithms=dna.algorithms,
            datasets=dna.datasets,
            research_papers=dna.research_papers,
            learning_order=dna.learning_order,
            mathematical_topics=dna.mathematical_topics,
            parent_topics=dna.parent_topics,
            child_topics=dna.child_topics,
            sibling_topics=dna.sibling_topics,
            research_evolution=dna.research_evolution,
            related_documents=[
                {
                    "id": item.related_document_id,
                    "title": item.title,
                    "similarity_score": item.similarity_score,
                    "shared_signals": item.shared_signals,
                }
                for item in dna.related_documents
            ],
        )

    def _sync_node_metadata(self, node: GraphNode) -> None:
        desired = {
            key: (self._metadata_value(value), self._metadata_type(value))
            for key, value in sorted(node.metadata_json.items())
        }
        existing = {item.metadata_key: item for item in list(node.metadata_items)}
        for key, (metadata_value, value_type) in desired.items():
            item = existing.get(key)
            if item is None:
                node.metadata_items.append(
                    NodeMetadata(
                        metadata_key=key,
                        metadata_value=metadata_value,
                        value_type=value_type,
                        confidence_score=1.0,
                    )
                )
            else:
                item.metadata_value = metadata_value
                item.value_type = value_type
                item.confidence_score = 1.0
        for key, item in existing.items():
            if key not in desired:
                node.metadata_items.remove(item)
                self.session.delete(item)

    def _sync_edge_metadata(self, edge: GraphEdge) -> None:
        desired = {
            key: (self._metadata_value(value), self._metadata_type(value))
            for key, value in sorted(edge.metadata_json.items())
        }
        existing = {item.metadata_key: item for item in list(edge.metadata_items)}
        for key, (metadata_value, value_type) in desired.items():
            item = existing.get(key)
            if item is None:
                edge.metadata_items.append(
                    RelationshipMetadata(
                        metadata_key=key,
                        metadata_value=metadata_value,
                        value_type=value_type,
                        confidence_score=1.0,
                    )
                )
            else:
                item.metadata_value = metadata_value
                item.value_type = value_type
                item.confidence_score = 1.0
        for key, item in existing.items():
            if key not in desired:
                edge.metadata_items.remove(item)
                self.session.delete(item)

    def _metadata_value(self, value: object) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, sort_keys=True)

    def _metadata_type(self, value: object) -> str:
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "object"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int | float):
            return "number"
        return "string"

    def _source_ids(self, metadata: dict[str, object]) -> list[str]:
        value = metadata.get("source_document_ids", [])
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            return [value]
        return []

    def _document(self, document_id: str) -> Document:
        document = self.documents.get_full(document_id)
        if document is None:
            raise NotFoundError("Document was not found.")
        return document

    def _node_draft(self, node: GraphNode) -> GraphNodeDraft:
        return GraphNodeDraft(
            stable_key=node.stable_key,
            node_type=node.node_type,
            name=node.name,
            label=node.label,
            description=node.description,
            importance_score=node.importance_score,
            confidence_score=node.confidence_score,
            size=node.size,
            color=node.color,
            metadata=node.metadata_json,
        )

    def _edge_draft(self, edge: GraphEdge) -> GraphEdgeDraft:
        return GraphEdgeDraft(
            stable_key=edge.stable_key,
            source_key=edge.source_node.stable_key,
            target_key=edge.target_node.stable_key,
            relationship_type=edge.relationship_type,
            label=edge.label,
            description=edge.description,
            weight=edge.weight,
            confidence_score=edge.confidence_score,
            metadata=edge.metadata_json,
        )

    def _graph_payload(self, graph: GraphRead) -> dict[str, Any]:
        return {
            "nodes": [node.model_dump(mode="json") for node in graph.nodes],
            "edges": [edge.model_dump(mode="json") for edge in graph.edges],
            "layout": graph.layout.model_dump(mode="json") if graph.layout else {"positions": []},
            "analytics": graph.analytics.model_dump(mode="json"),
            "insights": graph.insights,
            "interaction": graph.interaction,
        }
