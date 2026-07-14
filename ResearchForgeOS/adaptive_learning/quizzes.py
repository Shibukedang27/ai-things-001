from __future__ import annotations

from adaptive_learning.types import CardDifficulty, LearningSource, QuizDraft, QuizQuestionDraft, QuizQuestionType
from adaptive_learning.utils import dedupe


class QuizEngine:
    def generate(
        self,
        source: LearningSource,
        *,
        difficulty: CardDifficulty | None = None,
        limit: int = 14,
    ) -> QuizDraft:
        target_difficulty = difficulty or self._source_difficulty(source)
        questions: list[QuizQuestionDraft] = []
        questions.extend(self._mcq_questions(source, target_difficulty))
        questions.extend(self._multiple_correct_questions(source, target_difficulty))
        questions.extend(self._fill_blank_questions(source, target_difficulty))
        questions.extend(self._code_completion_questions(source, target_difficulty))
        questions.extend(self._scenario_questions(source, target_difficulty))
        questions.extend(self._case_study_questions(source, target_difficulty))
        questions.extend(self._research_questions(source, target_difficulty))
        questions.extend(self._debugging_questions(source, target_difficulty))
        questions.extend(self._algorithm_questions(source, target_difficulty))
        return QuizDraft(
            title=f"{source.title} Adaptive Knowledge Test",
            quiz_type="adaptive_timed",
            difficulty=target_difficulty,
            time_limit_seconds=max(600, min(3600, len(questions[:limit]) * 90)),
            adaptive=True,
            questions=questions[:limit],
            metadata={"document_id": source.document_id, "engine": "adaptive_quiz_v1"},
        )

    def grade(self, questions: list[dict[str, object]], answers: dict[str, object]) -> dict[str, object]:
        total_points = sum(int(question.get("points", 1)) for question in questions)
        earned = 0
        feedback: list[dict[str, object]] = []
        for question in questions:
            question_id = str(question["id"])
            correct_answers = [str(item).casefold() for item in question.get("correct_answers", [])]
            submitted = answers.get(question_id, [])
            submitted_answers = submitted if isinstance(submitted, list) else [submitted]
            normalized = [str(item).casefold() for item in submitted_answers]
            is_correct = bool(correct_answers) and set(normalized) == set(correct_answers)
            points = int(question.get("points", 1))
            if is_correct:
                earned += points
            feedback.append(
                {
                    "question_id": question_id,
                    "correct": is_correct,
                    "earned_points": points if is_correct else 0,
                    "possible_points": points,
                    "correct_answers": question.get("correct_answers", []),
                    "explanation": question.get("explanation", ""),
                }
            )
        accuracy = 0.0 if total_points == 0 else round(earned / total_points, 4)
        return {
            "score": earned,
            "total_points": total_points,
            "accuracy": accuracy,
            "passed": accuracy >= 0.7,
            "feedback": feedback,
        }

    def _mcq_questions(self, source: LearningSource, difficulty: CardDifficulty) -> list[QuizQuestionDraft]:
        concepts = source.concepts[:5]
        names = [concept.name for concept in concepts]
        questions: list[QuizQuestionDraft] = []
        for concept in concepts:
            distractors = [name for name in names if name != concept.name][:3]
            while len(distractors) < 3:
                distractors.append(
                    source.category if len(distractors) == 0 else f"{source.category} detail {len(distractors)}"
                )
            questions.append(
                QuizQuestionDraft(
                    question_type=QuizQuestionType.MCQ,
                    prompt=f"Which option best matches this description: {concept.description[:220]}",
                    choices=dedupe([concept.name, *distractors])[:4],
                    correct_answers=[concept.name],
                    explanation=concept.description,
                    difficulty=difficulty,
                    points=self._points(difficulty),
                    metadata={"concept": concept.name},
                )
            )
        return questions

    def _multiple_correct_questions(
        self,
        source: LearningSource,
        difficulty: CardDifficulty,
    ) -> list[QuizQuestionDraft]:
        if not source.technologies and len(source.concepts) < 2:
            return []
        correct = dedupe([*source.technologies[:3], *[concept.name for concept in source.concepts[:2]]])
        choices = dedupe([*correct, "Unrelated archive topic", "Purely decorative UI element"])[:6]
        return [
            QuizQuestionDraft(
                question_type=QuizQuestionType.MULTIPLE_CORRECT,
                prompt=f"Select all items directly connected to {source.title}.",
                choices=choices,
                correct_answers=correct[: len(choices)],
                explanation="The correct answers are concepts or technologies extracted from the source.",
                difficulty=difficulty,
                points=self._points(difficulty) + 1,
                metadata={"document_id": source.document_id},
            )
        ]

    def _fill_blank_questions(self, source: LearningSource, difficulty: CardDifficulty) -> list[QuizQuestionDraft]:
        return [
            QuizQuestionDraft(
                question_type=QuizQuestionType.FILL_BLANK,
                prompt=f"Fill in the blank: ____ is a key concept in {source.title}.",
                choices=[],
                correct_answers=[concept.name],
                explanation=concept.description,
                difficulty=difficulty,
                points=self._points(difficulty),
                metadata={"concept": concept.name},
            )
            for concept in source.concepts[5:8]
        ]

    def _code_completion_questions(self, source: LearningSource, difficulty: CardDifficulty) -> list[QuizQuestionDraft]:
        questions: list[QuizQuestionDraft] = []
        for snippet in source.code_snippets[:2]:
            language = snippet.get("language") or "code"
            code = snippet.get("code") or snippet.get("content") or ""
            if not code:
                continue
            questions.append(
                QuizQuestionDraft(
                    question_type=QuizQuestionType.CODE_COMPLETION,
                    prompt=f"Complete or explain the missing step in this {language} snippet: {str(code)[:400]}",
                    choices=[],
                    correct_answers=["Identify inputs, output, and the missing operation."],
                    explanation="A good answer explains the code path and the missing operation.",
                    difficulty=CardDifficulty.HARD,
                    points=4,
                    metadata={"language": language},
                )
            )
        return questions

    def _scenario_questions(self, source: LearningSource, difficulty: CardDifficulty) -> list[QuizQuestionDraft]:
        if not source.concepts:
            return []
        concept = source.concepts[0]
        return [
            QuizQuestionDraft(
                question_type=QuizQuestionType.SCENARIO,
                prompt=f"A team must apply {concept.name} in production. What trade-offs should they consider?",
                choices=[],
                correct_answers=["prerequisites", "constraints", "evaluation", "failure modes"],
                explanation="Strong answers cover constraints, assumptions, evaluation, and risks.",
                difficulty=CardDifficulty.HARD if difficulty != CardDifficulty.EXPERT else CardDifficulty.EXPERT,
                points=5,
                metadata={"concept": concept.name},
            )
        ]

    def _case_study_questions(self, source: LearningSource, difficulty: CardDifficulty) -> list[QuizQuestionDraft]:
        return [
            QuizQuestionDraft(
                question_type=QuizQuestionType.CASE_STUDY,
                prompt=(
                    f"Use {source.title} as a case study. "
                    "Summarize the problem, approach, evidence, and limitation."
                ),
                choices=[],
                correct_answers=["problem", "approach", "evidence", "limitation"],
                explanation="Case-study answers must identify the source's purpose and limits.",
                difficulty=difficulty,
                points=5,
                metadata={"document_id": source.document_id},
            )
        ]

    def _research_questions(self, source: LearningSource, difficulty: CardDifficulty) -> list[QuizQuestionDraft]:
        return [
            QuizQuestionDraft(
                question_type=QuizQuestionType.RESEARCH,
                prompt=f"What research question naturally follows from {source.title}?",
                choices=[],
                correct_answers=["extension", "evaluation", "comparison"],
                explanation="A strong research question proposes an extension, evaluation, or comparison.",
                difficulty=difficulty,
                points=4,
                metadata={"topics": source.topics[:5]},
            )
        ]

    def _debugging_questions(self, source: LearningSource, difficulty: CardDifficulty) -> list[QuizQuestionDraft]:
        if not source.technologies:
            return []
        technology = source.technologies[0]
        return [
            QuizQuestionDraft(
                question_type=QuizQuestionType.DEBUGGING,
                prompt=f"A {technology} implementation of {source.title} is failing. How would you debug it?",
                choices=[],
                correct_answers=["reproduce", "inspect inputs", "check assumptions", "test edge cases"],
                explanation="Debugging should move from reproduction to evidence and controlled fixes.",
                difficulty=CardDifficulty.MEDIUM,
                points=4,
                metadata={"technology": technology},
            )
        ]

    def _algorithm_questions(self, source: LearningSource, difficulty: CardDifficulty) -> list[QuizQuestionDraft]:
        return [
            QuizQuestionDraft(
                question_type=QuizQuestionType.ALGORITHM,
                prompt=f"Describe the algorithmic steps and complexity considerations for {name}.",
                choices=[],
                correct_answers=["steps", "complexity", "edge cases"],
                explanation=f"Answers should explain how {name} runs and what makes it efficient or difficult.",
                difficulty=CardDifficulty.HARD,
                points=5,
                metadata={"algorithm": name},
            )
            for item in source.algorithms[:3]
            if (name := str(item.get("name") or item.get("algorithm") or "the algorithm"))
        ]

    def _source_difficulty(self, source: LearningSource) -> CardDifficulty:
        normalized = source.difficulty.casefold()
        if normalized in {"expert", "advanced"}:
            return CardDifficulty.HARD if normalized == "advanced" else CardDifficulty.EXPERT
        if normalized == "beginner":
            return CardDifficulty.EASY
        return CardDifficulty.MEDIUM

    def _points(self, difficulty: CardDifficulty) -> int:
        return {
            CardDifficulty.EASY: 1,
            CardDifficulty.MEDIUM: 2,
            CardDifficulty.HARD: 3,
            CardDifficulty.EXPERT: 5,
        }[difficulty]
