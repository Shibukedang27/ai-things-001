from adaptive_learning import AdaptiveLearningEngine, SpacedRepetitionScheduler
from adaptive_learning.types import CardDifficulty, LearningConcept, LearningSource, ReviewRating


def learning_source() -> LearningSource:
    return LearningSource(
        document_id="doc-adaptive-learning",
        title="Transformer Attention Systems",
        category="Machine Learning",
        difficulty="advanced",
        topics=["Attention", "Transformers", "Sequence Modeling"],
        concepts=[
            LearningConcept(
                name="Self Attention",
                description="Self attention compares token representations to compute contextual relevance.",
                difficulty=CardDifficulty.HARD,
                keywords=["attention", "tokens"],
                source_excerpt="Self attention compares token representations.",
            ),
            LearningConcept(
                name="Positional Encoding",
                description="Positional encoding injects order information into transformer inputs.",
                difficulty=CardDifficulty.MEDIUM,
                keywords=["position", "sequence"],
                source_excerpt="Positional encoding injects order.",
            ),
            LearningConcept(
                name="Multi Head Attention",
                description="Multi head attention learns several attention projections in parallel.",
                difficulty=CardDifficulty.HARD,
                keywords=["projection", "parallel"],
                source_excerpt="Multi head attention learns several projections.",
            ),
        ],
        keywords=["attention", "transformer", "embedding"],
        technologies=["PyTorch", "FastAPI"],
        definitions=[{"term": "Transformer", "definition": "A neural architecture based on attention layers."}],
        algorithms=[{"name": "Scaled Dot Product Attention", "description": "Compute QK scores and weight values."}],
        equations=[{"name": "attention", "equation": "softmax(QK^T / sqrt(d_k))V"}],
        code_snippets=[{"language": "python", "code": "scores = q @ k.T"}],
        summaries={"technical": "Attention computes contextual token relevance."},
        learning_objectives=["Explain attention", "Implement a small attention scorer"],
        cleaned_text=(
            "Self Attention compares token representations. Positional Encoding injects order information. "
            "Scaled Dot Product Attention uses softmax(QK^T / sqrt(d_k))V."
        ),
    )


def test_adaptive_learning_engine_generates_complete_bundle() -> None:
    bundle = AdaptiveLearningEngine().build(learning_source())
    card_types = {card.card_type.value for card in bundle.flashcards}
    question_types = {question.question_type.value for question in bundle.quiz.questions}

    assert {"definition", "concept", "formula", "algorithm", "code", "interview", "true_false"}.issubset(card_types)
    assert {"mcq", "multiple_correct", "scenario", "case_study", "research", "algorithm"}.issubset(question_types)
    assert bundle.quiz.adaptive is True
    assert bundle.interview_questions
    assert bundle.coding_challenges
    assert {plan.plan_type.value for plan in bundle.revision_plans} == {
        "daily",
        "weekly",
        "monthly",
        "quick",
        "exam",
        "interview",
        "coding",
    }
    assert bundle.analytics.knowledge_score >= 0
    assert bundle.achievements


def test_spaced_repetition_scheduler_updates_memory_state() -> None:
    scheduler = SpacedRepetitionScheduler()
    initial = scheduler.initial_state()
    reviewed = scheduler.schedule(initial, ReviewRating.GOOD, confidence=0.82)

    assert reviewed.review_count == 1
    assert reviewed.success_rate == 1.0
    assert reviewed.memory_strength > initial.memory_strength
    assert reviewed.next_review_at is not None
    assert reviewed.mastery_percentage > initial.mastery_percentage
