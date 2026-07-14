import math

import networkx as nx

from graph_engine.types import GraphEdgeDraft, GraphLayoutItem, GraphNodeDraft


class LayoutManager:
    def layout(self, nodes: list[GraphNodeDraft], edges: list[GraphEdgeDraft]) -> list[GraphLayoutItem]:
        if not nodes:
            return []
        graph = nx.Graph()
        for node in nodes:
            graph.add_node(node.stable_key)
        for edge in edges:
            graph.add_edge(edge.source_key, edge.target_key, weight=max(edge.weight, 0.1))

        if len(nodes) <= 2:
            positions = self._line_layout(nodes)
        elif len(nodes) > 1800:
            positions = self._radial_layout(nodes)
        else:
            positions = nx.spring_layout(graph, seed=42, k=self._spring_distance(len(nodes)), iterations=80)

        return [
            GraphLayoutItem(
                stable_key=node.stable_key,
                x=round(float(positions[node.stable_key][0]) * 1200, 3),
                y=round(float(positions[node.stable_key][1]) * 1200, 3),
            )
            for node in nodes
        ]

    def _spring_distance(self, node_count: int) -> float:
        return max(0.08, min(0.5, 1 / math.sqrt(node_count)))

    def _line_layout(self, nodes: list[GraphNodeDraft]) -> dict[str, tuple[float, float]]:
        return {node.stable_key: (index * 0.4, 0.0) for index, node in enumerate(nodes)}

    def _radial_layout(self, nodes: list[GraphNodeDraft]) -> dict[str, tuple[float, float]]:
        positions: dict[str, tuple[float, float]] = {}
        radius = max(1.0, len(nodes) / 50)
        for index, node in enumerate(nodes):
            angle = 2 * math.pi * index / len(nodes)
            positions[node.stable_key] = (math.cos(angle) * radius, math.sin(angle) * radius)
        return positions


class InteractionManager:
    def interaction_payload(self, node_count: int, edge_count: int) -> dict[str, object]:
        return {
            "visualization_library": "cytoscape.js-compatible",
            "supports": {
                "zoom": True,
                "pan": True,
                "drag_nodes": True,
                "collapse_groups": True,
                "expand_groups": True,
                "node_search": True,
                "filter": True,
                "highlight_paths": True,
                "auto_layout": True,
                "smooth_animation": True,
                "mini_map": True,
                "legend": True,
                "export_png": True,
                "export_svg": True,
                "export_json": True,
            },
            "performance": {
                "lazy_loading": node_count > 350,
                "virtual_rendering_recommended": node_count > 1000 or edge_count > 3000,
                "initial_node_limit": min(node_count, 500),
                "expand_depth_default": 1,
            },
            "legend": self._legend(),
        }

    def _legend(self) -> list[dict[str, str]]:
        return [
            {"type": "document", "label": "Document", "color": "#2563eb"},
            {"type": "concept", "label": "Concept", "color": "#059669"},
            {"type": "technology", "label": "Technology", "color": "#0891b2"},
            {"type": "algorithm", "label": "Algorithm", "color": "#dc2626"},
            {"type": "research_paper", "label": "Research Paper", "color": "#7c3aed"},
            {"type": "author", "label": "Author", "color": "#db2777"},
        ]
