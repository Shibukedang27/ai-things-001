from graph_engine import GraphBuildInput, InteractiveKnowledgeGraphEngine
from graph_engine.types import (
    GraphConceptInput,
    GraphDNAInput,
    GraphDocumentInput,
    GraphReferenceInput,
    GraphRelationshipInput,
    GraphTechnologyInput,
)


def sample_graph_input() -> GraphBuildInput:
    document = GraphDocumentInput(
        id="doc-attention",
        title="Attention Is All You Need",
        author="Ashish Vaswani",
        category="Research",
        source_type="research_paper",
        difficulty="advanced",
        created_at="2026-07-14",
        topics=["Transformers", "Attention"],
        keywords=["attention", "sequence modeling", "neural networks"],
        technologies=[
            GraphTechnologyInput(id="tech-pytorch", name="PyTorch", category="framework", confidence_score=0.82)
        ],
        concepts=[
            GraphConceptInput(
                id="concept-attention",
                name="Attention",
                concept_type="core",
                description="Mechanism for weighting token relationships.",
                prerequisites=["Backpropagation"],
                dependencies=["Embeddings"],
                difficulty_level="advanced",
                confidence_score=0.91,
            )
        ],
        algorithms=["Scaled Dot Product Attention"],
        references=[
            GraphReferenceInput(
                title="Attention Is All You Need",
                authors=["Ashish Vaswani"],
                year=2017,
                source="NeurIPS",
                url="https://example.com/attention",
                citation_text="Vaswani et al. Attention Is All You Need.",
                reference_type="research_paper",
                confidence_score=0.9,
            )
        ],
        relationships=[
            GraphRelationshipInput(
                source_name="Attention",
                target_name="Embeddings",
                relationship_type="depends_on",
                description="Attention depends on embeddings.",
                confidence_score=0.78,
            )
        ],
        cleaned_text="Google and OpenAI use Transformer attention models in modern AI systems.",
        dna=GraphDNAInput(
            primary_concepts=["Attention"],
            secondary_concepts=["Transformers"],
            prerequisites=["Backpropagation"],
            future_learning_topics=["Retrieval Augmented Generation"],
            programming_languages=["Python"],
            frameworks=["PyTorch"],
            algorithms=["Scaled Dot Product Attention"],
            research_papers=["BERT"],
        ),
    )
    return GraphBuildInput(document=document)


def test_interactive_graph_engine_generates_nodes_edges_layout_and_insights() -> None:
    result = InteractiveKnowledgeGraphEngine().build(sample_graph_input())

    node_keys = {node.stable_key for node in result.nodes}
    assert "document:doc-attention" in node_keys
    assert "concept:attention" in node_keys
    assert result.edges
    assert result.layout
    assert result.analytics["node_count"] == len(result.nodes)
    assert result.analytics["edge_count"] == len(result.edges)
    assert result.insights["most_connected_concepts"]
    assert result.interaction["supports"]["zoom"] is True
