from datetime import UTC, datetime

from workspace_engine import SmartNoteEngine, TaskAssistantEngine, WorkspaceSearchEngine, WritingAssistant
from workspace_engine.types import ChecklistType, SearchableNote, SearchMode, WritingMode


def test_smart_note_engine_generates_second_brain_metadata() -> None:
    engine = SmartNoteEngine()
    analysis = engine.analyze(
        """
        Transformer research notes: Attention mechanisms depend on embeddings and matrix multiplication.
        Action: compare Retrieval Augmented Generation with long context models.
        FastAPI and PostgreSQL will store the workspace memory.
        """,
        tags=["transformers"],
    )

    assert analysis.title
    assert analysis.summary
    assert "transformers" in analysis.tags
    assert analysis.keywords
    assert analysis.concepts
    assert analysis.action_items
    assert len(analysis.content_hash) == 64


def test_workspace_search_supports_hybrid_keyword_and_concept_matching() -> None:
    note = SearchableNote(
        id="note-1",
        title="Transformer Research Plan",
        content="Study attention, embeddings, and Retrieval Augmented Generation.",
        summary="A plan for attention and RAG.",
        tags=["transformer", "rag"],
        keywords=["attention", "embeddings"],
        concepts=["Attention", "Retrieval Augmented Generation"],
        category="Research",
        author="Research Owner",
        project_id="project-1",
        collection_id="collection-1",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    results = WorkspaceSearchEngine().search(
        "attention rag",
        [note],
        mode=SearchMode.HYBRID,
        tags=["rag"],
        project_id="project-1",
        concepts=["Attention"],
    )

    assert len(results) == 1
    assert results[0].note_id == "note-1"
    assert results[0].score > 0
    assert "concepts" in results[0].matched_fields


def test_writing_and_task_assistants_generate_structured_outputs() -> None:
    writing = WritingAssistant().assist(
        "transformers use attention to connect tokens with context",
        mode=WritingMode.TECHNICAL,
    )
    assert "Technical Explanation" in writing.output_text
    assert writing.changes

    plan = TaskAssistantEngine().generate_plan(
        "Build a research implementation plan for vector search and citations.",
        plan_type=ChecklistType.IMPLEMENTATION,
        concepts=["Vector Search"],
    )
    assert plan.title.startswith("Vector Search")
    assert plan.checklist
    assert plan.estimated_days >= 1
