from graph_engine import InteractiveKnowledgeGraphEngine
from tests.test_interactive_graph_engine import sample_graph_input


def test_graph_engine_outputs_no_duplicate_nodes_or_orphan_edges() -> None:
    result = InteractiveKnowledgeGraphEngine().build(sample_graph_input())
    node_keys = [node.stable_key for node in result.nodes]
    node_key_set = set(node_keys)
    edge_keys = [edge.stable_key for edge in result.edges]

    assert len(node_keys) == len(node_key_set)
    assert len(edge_keys) == len(set(edge_keys))
    assert all(edge.source_key in node_key_set for edge in result.edges)
    assert all(edge.target_key in node_key_set for edge in result.edges)
    assert all(edge.source_key != edge.target_key for edge in result.edges)
