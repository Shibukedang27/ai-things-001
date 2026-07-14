from knowledge_engine.types import ConceptCandidate, LearningAssets, SummaryBundle, TechnologyCandidate


class LearningAssetGenerator:
    def generate(
        self,
        *,
        concepts: list[ConceptCandidate],
        technologies: list[TechnologyCandidate],
        summaries: SummaryBundle,
    ) -> LearningAssets:
        core_concepts = concepts[:8]
        learning_objectives = [
            f"Explain {concept.name} and why it matters in this source."
            for concept in core_concepts[:6]
        ]
        if technologies:
            learning_objectives.append(
                "Identify where the source depends on "
                + ", ".join(technology.name for technology in technologies[:4])
                + "."
            )

        flashcards = [
            {
                "front": f"What is {concept.name}?",
                "back": concept.description[:360],
            }
            for concept in core_concepts[:10]
        ]

        quiz_questions = [
            {
                "question": f"Which statement best describes {concept.name}?",
                "answer": concept.description[:240],
                "difficulty": concept.difficulty_level.value,
            }
            for concept in core_concepts[:8]
        ]

        interview_questions = [
            f"How would you apply {concept.name} in a real project or research workflow?"
            for concept in core_concepts[:6]
        ]

        daily_revision_plan = [
            "Day 1: Read the executive summary and list the core concepts from memory.",
            "Day 2: Review definitions and explain each concept in plain language.",
            "Day 3: Connect concepts to technologies, algorithms, equations, or code examples.",
            "Day 4: Answer quiz questions without looking at the source.",
            "Day 5: Rebuild the concept relationships and revisit weak areas.",
        ]
        if summaries.five_minute_summary:
            daily_revision_plan.append("Day 6: Teach the five-minute summary as a short verbal walkthrough.")

        return LearningAssets(
            learning_objectives=learning_objectives,
            flashcards=flashcards,
            quiz_questions=quiz_questions,
            interview_questions=interview_questions,
            daily_revision_plan=daily_revision_plan,
        )
