import time

from graph_engine.layout import LayoutManager
from graph_engine.types import GraphEdgeDraft, GraphNodeDraft


def test_layout_manager_handles_thousands_of_nodes_quickly() -> None:
    nodes = [
        GraphNodeDraft(
            stable_key=f"concept:node-{index}",
            node_type="concept",
            name=f"Node {index}",
            label=f"Node {index}",
            description="Synthetic graph node.",
            importance_score=0.5,
            confidence_score=0.7,
            size=24,
            color="#059669",
            metadata={},
        )
        for index in range(2200)
    ]
    edges = [
        GraphEdgeDraft(
            stable_key=f"edge-{index}",
            source_key=f"concept:node-{index}",
            target_key=f"concept:node-{index + 1}",
            relationship_type="related_to",
            label="Related To",
            description="Synthetic relationship.",
            weight=0.5,
            confidence_score=0.7,
            metadata={},
        )
        for index in range(2199)
    ]

    started_at = time.perf_counter()
    layout = LayoutManager().layout(nodes, edges)
    duration = time.perf_counter() - started_at

    assert len(layout) == len(nodes)
    assert duration < 2.0
