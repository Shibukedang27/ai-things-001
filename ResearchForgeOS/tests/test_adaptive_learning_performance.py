from time import perf_counter

from adaptive_learning import AdaptiveLearningEngine
from adaptive_learning.types import CardDifficulty, LearningConcept, LearningSource


def test_adaptive_learning_engine_performance() -> None:
    concepts = [
        LearningConcept(
            name=f"Concept {index}",
            description=f"Concept {index} describes a reusable research learning unit.",
            difficulty=CardDifficulty.MEDIUM,
            keywords=["research", "learning"],
            source_excerpt=f"Concept {index} describes a reusable research learning unit.",
        )
        for index in range(100)
    ]
    source = LearningSource(
        document_id="performance-doc",
        title="Large Learning Corpus",
        category="Research",
        difficulty="intermediate",
        topics=[concept.name for concept in concepts[:20]],
        concepts=concepts,
        keywords=["retrieval", "knowledge", "testing"],
        technologies=["Python"],
        definitions=[{"term": "Learning Unit", "definition": "A structured piece of knowledge."}],
        algorithms=[{"name": "Review Scheduler", "description": "Schedules memory reviews."}],
        equations=[],
        code_snippets=[],
        summaries={"technical": "A large corpus for performance validation."},
        learning_objectives=["Build learning assets quickly"],
        cleaned_text=" ".join(concept.description for concept in concepts),
    )

    started = perf_counter()
    bundle = AdaptiveLearningEngine().build(source)
    elapsed = perf_counter() - started

    assert len(bundle.flashcards) <= 48
    assert len(bundle.quiz.questions) <= 14
    assert elapsed < 2.0
