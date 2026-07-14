"""Question generation providers for the interview engine."""

from dataclasses import dataclass

from app.domain.enums import DifficultyLevel
from app.schemas.interview_engine import EngineQuestionCategory


@dataclass(frozen=True)
class GeneratedInterviewQuestion:
    """Generated question payload."""

    category: EngineQuestionCategory
    difficulty: DifficultyLevel
    prompt: str
    expected_signal: str
    tags: list[str]


class InterviewQuestionGenerator:
    """Question generator interface."""

    async def generate(
        self,
        *,
        role: str,
        difficulty: DifficultyLevel,
        categories: list[EngineQuestionCategory],
        question_count: int,
    ) -> list[GeneratedInterviewQuestion]:
        raise NotImplementedError


class TemplateAIQuestionGenerator(InterviewQuestionGenerator):
    """Deterministic AI-style generator used until an external AI provider is configured."""

    _templates: dict[EngineQuestionCategory, list[str]] = {
        EngineQuestionCategory.PYTHON: [
            "For a {role} role, how would you design a Python module that is easy to test, type-check, and extend?",
            "Walk through how you would debug a Python service with intermittent latency spikes in production.",
            "Explain how you use generators, context managers, and async code in Python, including tradeoffs.",
        ],
        EngineQuestionCategory.JAVA: [
            "For a {role} role, explain how you would structure a Java service for maintainability and clear domain boundaries.",
            "How would you diagnose memory pressure in a Java application running under production traffic?",
            "Compare Java concurrency primitives you would consider for a high-throughput backend workflow.",
        ],
        EngineQuestionCategory.SQL: [
            "Given a slow SQL query in a candidate-facing product, how would you investigate and optimize it?",
            "Design a relational schema for tracking interview sessions, answers, and reports. Explain your indexes.",
            "How would you ensure correctness when multiple workers update SQL-backed interview state concurrently?",
        ],
        EngineQuestionCategory.DSA: [
            "Describe how you would choose between a hash map, heap, tree, and graph traversal for a new problem.",
            "Solve a problem where you must find the top K recurring interview topics from a stream of events.",
            "Explain how you reason about time and space complexity when optimizing a data structure.",
        ],
        EngineQuestionCategory.SYSTEM_DESIGN: [
            "Design a scalable interview practice platform for thousands of concurrent mock interviews.",
            "How would you design reliable question generation, answer storage, and session recovery for this product?",
            "Design observability and failure handling for a real-time interview engine.",
        ],
        EngineQuestionCategory.MACHINE_LEARNING: [
            "How would you build and validate an ML model that predicts candidate readiness from practice data?",
            "Explain how you would prevent data leakage in an interview-performance ML pipeline.",
            "What metrics would you track for an ML feature that recommends personalized practice questions?",
        ],
        EngineQuestionCategory.DEEP_LEARNING: [
            "Explain how you would fine-tune a deep learning model while controlling overfitting and cost.",
            "How would you evaluate a neural model used to classify answer quality without building final evaluation yet?",
            "Describe the tradeoffs between transformer fine-tuning, retrieval augmentation, and prompt-only approaches.",
        ],
        EngineQuestionCategory.NLP: [
            "How would you extract structured signals from free-form interview answers using NLP techniques?",
            "Explain how you would handle ambiguity, filler words, and incomplete sentences in answer transcripts.",
            "Design an NLP pipeline for detecting topics covered in a candidate's response.",
        ],
        EngineQuestionCategory.PROMPT_ENGINEERING: [
            "How would you design prompts that generate role-specific interview questions consistently?",
            "Explain how you would test and version prompts for an AI interview product.",
            "How would you reduce hallucination risk when prompting a model to generate technical interview questions?",
        ],
        EngineQuestionCategory.BEHAVIORAL: [
            "Tell me about a time you handled ambiguity while delivering an important project.",
            "Describe a conflict with a teammate and how you resolved it.",
            "Give an example of a decision you made with incomplete information.",
        ],
        EngineQuestionCategory.HR: [
            "Why are you interested in this role, and what would make it a strong fit for you?",
            "What are your compensation, location, and work-style expectations for this opportunity?",
            "How do you describe your ideal manager and team environment?",
        ],
    }

    async def generate(
        self,
        *,
        role: str,
        difficulty: DifficultyLevel,
        categories: list[EngineQuestionCategory],
        question_count: int,
    ) -> list[GeneratedInterviewQuestion]:
        questions: list[GeneratedInterviewQuestion] = []
        for index in range(question_count):
            category = categories[index % len(categories)]
            templates = self._templates[category]
            template = templates[(index // len(categories)) % len(templates)]
            rendered_prompt = template.format(role=role)
            if role not in rendered_prompt:
                rendered_prompt = f"For a {role} role, {rendered_prompt[0].lower()}{rendered_prompt[1:]}"
            prompt = f"[{difficulty.value.title()}] {rendered_prompt}"
            questions.append(
                GeneratedInterviewQuestion(
                    category=category,
                    difficulty=difficulty,
                    prompt=prompt,
                    expected_signal=self._expected_signal(category),
                    tags=[category.value, difficulty.value, "ai_generated"],
                )
            )
        return questions

    def _expected_signal(self, category: EngineQuestionCategory) -> str:
        return {
            EngineQuestionCategory.PYTHON: "python_engineering_depth",
            EngineQuestionCategory.JAVA: "java_engineering_depth",
            EngineQuestionCategory.SQL: "database_reasoning",
            EngineQuestionCategory.DSA: "algorithmic_reasoning",
            EngineQuestionCategory.SYSTEM_DESIGN: "architecture_tradeoffs",
            EngineQuestionCategory.MACHINE_LEARNING: "ml_reasoning",
            EngineQuestionCategory.DEEP_LEARNING: "deep_learning_reasoning",
            EngineQuestionCategory.NLP: "nlp_reasoning",
            EngineQuestionCategory.PROMPT_ENGINEERING: "prompt_design",
            EngineQuestionCategory.BEHAVIORAL: "behavioral_signal",
            EngineQuestionCategory.HR: "role_fit",
        }[category]
