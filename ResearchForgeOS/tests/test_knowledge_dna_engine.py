from knowledge_engine.dna import KnowledgeDNAEngine
from knowledge_engine.dna.types import DNAConceptInput, DNADocumentInput, DNATechnologyInput, RelatedDocumentCandidate


def test_knowledge_dna_engine_generates_graph_and_learning_path() -> None:
    document = DNADocumentInput(
        id="doc_attention",
        title="Attention Is All You Need",
        category="Research",
        difficulty="advanced",
        estimated_reading_time_minutes=18,
        word_count=4800,
        topics=["Attention", "Transformers", "Neural Networks"],
        keywords=["attention", "transformer", "embedding", "sequence modeling"],
        concepts=[
            DNAConceptInput(
                id="c1",
                name="Attention",
                concept_type="core",
                description="Attention is a mechanism for weighting token relationships.",
                prerequisites=["Neural Networks"],
                dependencies=["Backpropagation"],
                difficulty_level="advanced",
                confidence_score=0.94,
            ),
            DNAConceptInput(
                id="c2",
                name="Transformer",
                concept_type="core",
                description="Transformer architecture uses attention for sequence modeling.",
                prerequisites=["Attention"],
                dependencies=["Embeddings"],
                difficulty_level="advanced",
                confidence_score=0.92,
            ),
        ],
        technologies=[DNATechnologyInput("t1", "PyTorch", "ml_framework", 0.86, ["PyTorch implementation"])],
        algorithms=["Gradient Descent Algorithm"],
        definitions=["Attention"],
        equations=["loss = y - prediction / batch_size"],
        code_snippet_count=1,
        references=["Vaswani et al. (2017). Attention Is All You Need."],
        cleaned_text="Attention transformers use embeddings, gradient optimization, and neural networks.",
        related_document_candidates=[
            RelatedDocumentCandidate(
                id="doc_gpt",
                title="GPT Architecture",
                category="Research",
                topics=["Transformers", "Language Models"],
                concepts=["Attention", "Autoregressive Modeling"],
                technologies=["PyTorch"],
            )
        ],
    )

    result = KnowledgeDNAEngine().generate(document)

    assert result.document_title == "Attention Is All You Need"
    assert result.research_category == "Artificial Intelligence"
    assert result.knowledge_score > 0.5
    assert "Attention" in result.primary_concepts
    assert "Neural Networks" in result.prerequisites
    assert "GPT" in result.future_learning_topics
    assert "PyTorch" in result.frameworks or "PyTorch" in result.libraries
    assert result.learning_path
    assert result.nodes
    assert result.edges
    assert result.related_documents
