from knowledge_engine import KnowledgeEnginePipeline, KnowledgeSourceRequest, SourceType

SAMPLE_MARKDOWN = """
# Vector Search Architecture

Vector Search Architecture is a retrieval technique for finding semantically similar knowledge chunks.
FastAPI coordinates the API layer, PostgreSQL stores document metadata, and JWT protects access.
Embeddings are generated for each chunk so that related concepts can be connected later.

The Chunk Manager is responsible for splitting content into stable pieces.
Gradient Descent Algorithm is used in many machine learning systems.
The loss equation is loss = y - prediction / batch_size.

```python
def embed(text: str) -> list[float]:
    return [1.0]
```

References
- Smith, J. (2024). "Vector Databases in Practice". https://example.com/vector
"""


def test_pipeline_generates_knowledge_object() -> None:
    pipeline = KnowledgeEnginePipeline()
    result = pipeline.process(
        KnowledgeSourceRequest(
            source_type=SourceType.MARKDOWN,
            filename="vector-search.md",
            content=SAMPLE_MARKDOWN,
            category="Engineering",
        )
    )

    assert result.metadata.title == "Vector Search Architecture"
    assert result.metadata.category == "Engineering"
    assert result.chunks
    assert result.embeddings
    assert result.summaries.executive_summary
    assert result.concepts
    assert result.keywords
    assert any(technology.name == "FastAPI" for technology in result.technologies)
    assert result.code_snippets
    assert result.references
    assert result.learning_assets.learning_objectives
