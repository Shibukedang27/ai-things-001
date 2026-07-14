import pytest
from ai.agents import AgentOrchestrator
from ai.agents.core.types import AgentDNA, AgentDocument, AgentExecutionContext, PipelineStatus


@pytest.mark.asyncio
async def test_orchestrator_runs_all_specialized_agents() -> None:
    document = AgentDocument(
        id="doc_1",
        title="Transformer Research Notes",
        category="Artificial Intelligence",
        difficulty="advanced",
        estimated_reading_time_minutes=12,
        topics=["Attention", "Transformers"],
        cleaned_text="Attention and transformers connect neural networks, embeddings, and optimization.",
        summaries={
            "executive": "Transformers use attention to model relationships in sequences.",
            "technical": "The document discusses attention, embeddings, and optimization.",
            "detailed": "Detailed transformer notes.",
            "one_minute": "Attention helps models focus on relevant tokens.",
            "five_minute": "Transformers combine attention, embeddings, and training objectives.",
        },
        concepts=[
            {
                "id": "c1",
                "name": "Attention",
                "concept_type": "core",
                "description": "Attention weights token relationships.",
                "prerequisites": ["Neural Networks"],
                "dependencies": ["Backpropagation"],
                "difficulty_level": "advanced",
                "confidence_score": 0.9,
            }
        ],
        keywords=["attention", "transformer"],
        technologies=[{"id": "t1", "name": "PyTorch", "category": "ml_framework", "confidence_score": 0.8}],
        algorithms=["Gradient Descent Algorithm"],
        definitions=[{"term": "Attention", "definition": "A token relationship mechanism."}],
        code_snippets=[{"language": "python", "code": "print('attention')"}],
        references=[{"title": "Attention Is All You Need", "year": 2017, "url": "https://example.com"}],
    )
    dna = AgentDNA(
        id="dna_1",
        research_category="Artificial Intelligence",
        knowledge_score=0.9,
        interview_importance=0.88,
        industry_relevance=0.8,
        implementation_complexity=0.72,
        primary_concepts=["Attention"],
        secondary_concepts=["Embeddings"],
        prerequisites=["Neural Networks", "Backpropagation"],
        future_learning_topics=["BERT", "GPT", "Retrieval Augmented Generation"],
        learning_order=["Neural Networks", "Backpropagation", "Attention", "BERT"],
        estimated_mastery_time_hours=12,
        parent_topics=["Neural Networks"],
        child_topics=["Scaled Dot Product Attention"],
        sibling_topics=["Convolution"],
        knowledge_chains=[["Neural Networks", "Attention", "BERT"]],
        research_evolution=["Neural Networks", "Attention", "GPT"],
    )

    result = await AgentOrchestrator().run(AgentExecutionContext(document=document, dna=dna))

    assert result.status == PipelineStatus.COMPLETED
    assert len(result.outputs) == 10
    assert result.final_response["quality_review"]["validation_status"] == "passed"
    assert any(output.role.value == "quality_assurance_agent" for output in result.outputs)
