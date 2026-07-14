from dataclasses import replace

from graph_engine.types import GraphEdgeDraft, GraphNodeDraft
from graph_engine.utils import merge_metadata, normalized_similarity, stable_edge_key


class DuplicateDetector:
    def duplicate_key(self, node: GraphNodeDraft) -> str:
        return node.stable_key

    def are_similar(self, left: GraphNodeDraft, right: GraphNodeDraft) -> bool:
        return left.node_type == right.node_type and normalized_similarity(left.name, right.name) >= 0.92


class NodeMerger:
    def __init__(self, detector: DuplicateDetector | None = None) -> None:
        self.detector = detector or DuplicateDetector()

    def merge(self, nodes: list[GraphNodeDraft]) -> list[GraphNodeDraft]:
        merged: dict[str, GraphNodeDraft] = {}
        for node in nodes:
            key = self.detector.duplicate_key(node)
            current = merged.get(key)
            if current is None:
                merged[key] = node
                continue
            merged[key] = replace(
                current,
                description=(
                    current.description
                    if len(current.description) >= len(node.description)
                    else node.description
                ),
                importance_score=max(current.importance_score, node.importance_score),
                confidence_score=max(current.confidence_score, node.confidence_score),
                size=max(current.size, node.size),
                metadata=merge_metadata(current.metadata, node.metadata),
            )
        return list(merged.values())


class RelationshipMerger:
    def merge(self, edges: list[GraphEdgeDraft], valid_node_keys: set[str]) -> list[GraphEdgeDraft]:
        merged: dict[str, GraphEdgeDraft] = {}
        for edge in edges:
            if edge.source_key == edge.target_key:
                continue
            if edge.source_key not in valid_node_keys or edge.target_key not in valid_node_keys:
                continue
            stable_key = stable_edge_key(edge.source_key, edge.target_key, edge.relationship_type)
            current = merged.get(stable_key)
            if current is None:
                merged[stable_key] = edge
                continue
            merged[stable_key] = replace(
                current,
                weight=max(current.weight, edge.weight),
                confidence_score=max(current.confidence_score, edge.confidence_score),
                metadata=merge_metadata(current.metadata, edge.metadata),
            )
        return list(merged.values())
