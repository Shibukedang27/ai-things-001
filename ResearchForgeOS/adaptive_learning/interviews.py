from __future__ import annotations

from adaptive_learning.types import CardDifficulty, InterviewQuestionDraft, InterviewQuestionType, LearningSource


class InterviewPreparationEngine:
    def generate(self, source: LearningSource) -> list[InterviewQuestionDraft]:
        questions: list[InterviewQuestionDraft] = [
            self._question(
                InterviewQuestionType.HR,
                CardDifficulty.EASY,
                f"Tell me about a time you learned a difficult topic like {source.title}.",
                "Use a concise situation, action, result, and reflection structure.",
            ),
            self._question(
                InterviewQuestionType.BEHAVIORAL,
                CardDifficulty.MEDIUM,
                f"How would you handle disagreement about the interpretation of {source.title}?",
                "Ground the discussion in evidence, assumptions, and measurable outcomes.",
            ),
        ]
        if source.concepts:
            concept = source.concepts[0]
            questions.extend(
                [
                    self._question(
                        InterviewQuestionType.TECHNICAL,
                        concept.difficulty,
                        f"Explain {concept.name} deeply enough for a senior technical interview.",
                        concept.description,
                    ),
                    self._question(
                        InterviewQuestionType.FOLLOW_UP,
                        CardDifficulty.HARD,
                        f"What follow-up questions would you ask after explaining {concept.name}?",
                        "Ask about constraints, alternatives, evaluation, and failure modes.",
                    ),
                ]
            )
        categories = self._category_questions(source)
        questions.extend(categories)
        return questions[:18]

    def _category_questions(self, source: LearningSource) -> list[InterviewQuestionDraft]:
        output: list[InterviewQuestionDraft] = []
        technology_text = " ".join(source.technologies).casefold()
        topic_text = " ".join(
            [source.category, *source.topics, *[concept.name for concept in source.concepts]]
        ).casefold()
        mapping = [
            ("python", InterviewQuestionType.PYTHON, "How would you implement the core idea in Python?"),
            ("java", InterviewQuestionType.JAVA, "How would you design a Java implementation for this topic?"),
            ("sql", InterviewQuestionType.SQL, "What SQL schema or query pattern would support this knowledge?"),
            ("backend", InterviewQuestionType.BACKEND, "How would this fit into a backend service architecture?"),
            ("nlp", InterviewQuestionType.NLP, "How does this relate to NLP systems and evaluation?"),
            ("generative", InterviewQuestionType.GENERATIVE_AI, "How does this shape generative AI system behavior?"),
            ("prompt", InterviewQuestionType.PROMPT_ENGINEERING, "How would prompts expose or test this concept?"),
            ("machine learning", InterviewQuestionType.MACHINE_LEARNING, "How would you evaluate this ML concept?"),
            ("system", InterviewQuestionType.SYSTEM_DESIGN, "Design a scalable system around this concept."),
        ]
        for marker, question_type, prompt in mapping:
            if marker in technology_text or marker in topic_text:
                output.append(
                    self._question(
                        question_type,
                        CardDifficulty.HARD
                        if question_type == InterviewQuestionType.SYSTEM_DESIGN
                        else CardDifficulty.MEDIUM,
                        prompt,
                        "A strong answer states assumptions, components, trade-offs, and evaluation criteria.",
                    )
                )
        if not output:
            output.append(
                self._question(
                    InterviewQuestionType.SYSTEM_DESIGN,
                    CardDifficulty.MEDIUM,
                    f"How would you build a learning workflow around {source.title}?",
                    "Use source ingestion, concept extraction, practice, review scheduling, and progress tracking.",
                )
            )
        return output

    def _question(
        self,
        question_type: InterviewQuestionType,
        difficulty: CardDifficulty,
        question: str,
        ideal_answer: str,
    ) -> InterviewQuestionDraft:
        return InterviewQuestionDraft(
            question_type=question_type,
            difficulty=difficulty,
            question=question,
            ideal_answer=ideal_answer,
            follow_ups=[
                "What assumptions are you making?",
                "How would you validate the answer?",
                "What would change at production scale?",
            ],
            evaluation_points=["clarity", "accuracy", "trade-offs", "evidence"],
            metadata={"engine": "interview_preparation_v1"},
        )
