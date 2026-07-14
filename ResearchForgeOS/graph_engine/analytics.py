from collections import Counter, defaultdict
from typing import Any

import networkx as nx

from graph_engine.types import GraphEdgeDraft, GraphNodeDraft, GraphRelationshipType


class GraphAnalyticsEngine:
    def analyze(self, nodes: list[GraphNodeDraft], edges: list[GraphEdgeDraft]) -> dict[str, Any]:
        graph = self._graph(nodes, edges)
        node_count = len(nodes)
        edge_count = len(edges)
        cluster_count = nx.number_connected_components(graph.to_undirected()) if node_count else 0
        density = nx.density(graph) if node_count > 1 else 0.0
        knowledge_score = self._knowledge_score(nodes, edge_count)
        coverage_score = self._coverage_score(nodes)
        mastery_score = round((knowledge_score * 0.48 + coverage_score * 0.34 + min(1.0, density * 8) * 0.18), 4)
        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "cluster_count": cluster_count,
            "graph_density": round(density, 6),
            "knowledge_score": knowledge_score,
            "coverage_score": coverage_score,
            "mastery_score": mastery_score,
            "learning_progress": round(min(1.0, (node_count / 150) * 0.55 + (edge_count / 300) * 0.45), 4),
            "average_degree": round((2 * edge_count / node_count), 4) if node_count else 0.0,
        }

    def insights(self, nodes: list[GraphNodeDraft], edges: list[GraphEdgeDraft]) -> dict[str, Any]:
        graph = self._graph(nodes, edges)
        node_lookup = {node.stable_key: node for node in nodes}
        degree = dict(graph.degree())
        most_connected = sorted(degree.items(), key=lambda item: item[1], reverse=True)[:10]
        relationship_counts = Counter(edge.relationship_type for edge in edges)
        type_counts = Counter(node.node_type for node in nodes)
        prerequisite_targets = Counter(
            edge.target_key for edge in edges if edge.relationship_type == GraphRelationshipType.PREREQUISITE.value
        )
        technology_nodes = [node for node in nodes if node.node_type in {"technology", "framework", "library"}]
        paper_nodes = [node for node in nodes if node.node_type == "research_paper"]
        missing_prerequisites = [
            edge.source_key
            for edge in edges
            if edge.relationship_type == GraphRelationshipType.PREREQUISITE.value and edge.source_key not in node_lookup
        ]
        learning_clusters = self._clusters(graph, node_lookup)
        return {
            "most_connected_concepts": [
                {
                    "stable_key": key,
                    "name": node_lookup[key].name,
                    "node_type": node_lookup[key].node_type,
                    "degree": value,
                }
                for key, value in most_connected
                if key in node_lookup
            ],
            "learning_bottlenecks": [
                {"stable_key": key, "name": node_lookup[key].name, "dependency_count": count}
                for key, count in prerequisite_targets.most_common(8)
                if key in node_lookup
            ],
            "emerging_topics": [
                node.name
                for node in sorted(nodes, key=lambda item: item.importance_score, reverse=True)
                if node.node_type in {"concept", "model", "algorithm"}
            ][:12],
            "frequently_used_technologies": [
                {"name": node.name, "importance_score": node.importance_score}
                for node in sorted(technology_nodes, key=lambda item: item.importance_score, reverse=True)[:10]
            ],
            "research_trends": [
                {"relationship_type": key, "count": count} for key, count in relationship_counts.most_common(10)
            ],
            "most_important_papers": [
                {"name": node.name, "importance_score": node.importance_score}
                for node in sorted(paper_nodes, key=lambda item: item.importance_score, reverse=True)[:10]
            ],
            "knowledge_growth_timeline": self._growth_timeline(nodes),
            "missing_prerequisites": missing_prerequisites[:10],
            "weak_knowledge_areas": [
                {"node_type": key, "count": count}
                for key, count in type_counts.items()
                if count < 2 and key in {"dataset", "algorithm", "research_paper"}
            ],
            "learning_clusters": learning_clusters,
        }

    def _graph(self, nodes: list[GraphNodeDraft], edges: list[GraphEdgeDraft]) -> nx.DiGraph:
        graph = nx.DiGraph()
        for node in nodes:
            graph.add_node(node.stable_key)
        for edge in edges:
            if edge.source_key in graph and edge.target_key in graph:
                graph.add_edge(edge.source_key, edge.target_key, weight=edge.weight)
        return graph

    def _knowledge_score(self, nodes: list[GraphNodeDraft], edge_count: int) -> float:
        if not nodes:
            return 0.0
        importance = sum(node.importance_score for node in nodes) / len(nodes)
        connectivity = min(1.0, edge_count / max(1, len(nodes) * 2))
        return round(importance * 0.7 + connectivity * 0.3, 4)

    def _coverage_score(self, nodes: list[GraphNodeDraft]) -> float:
        required_types = {
            "document",
            "concept",
            "technology",
            "algorithm",
            "research_paper",
            "author",
            "interview_topic",
        }
        present = {node.node_type for node in nodes}
        return round(len(required_types & present) / len(required_types), 4)

    def _clusters(self, graph: nx.DiGraph, node_lookup: dict[str, GraphNodeDraft]) -> list[dict[str, Any]]:
        clusters: list[dict[str, Any]] = []
        for index, component in enumerate(nx.connected_components(graph.to_undirected())):
            names = [node_lookup[key].name for key in component if key in node_lookup]
            clusters.append({"cluster_id": f"cluster-{index + 1}", "size": len(component), "sample_nodes": names[:8]})
        return sorted(clusters, key=lambda item: item["size"], reverse=True)[:12]

    def _growth_timeline(self, nodes: list[GraphNodeDraft]) -> list[dict[str, Any]]:
        timeline: dict[str, int] = defaultdict(int)
        for node in nodes:
            created_at = node.metadata.get("created_at")
            bucket = str(created_at)[:10] if created_at else "unknown"
            timeline[bucket] += 1
        return [{"date": key, "node_count": value} for key, value in sorted(timeline.items())]
