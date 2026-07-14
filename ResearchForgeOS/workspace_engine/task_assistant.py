from __future__ import annotations

from workspace_engine.types import ChecklistType, TaskPlan
from workspace_engine.utils import dedupe, extract_concepts, normalize_space, top_keywords


class TaskAssistantEngine:
    def generate_plan(
        self,
        prompt: str,
        *,
        plan_type: ChecklistType,
        concepts: list[str] | None = None,
        resources: list[str] | None = None,
    ) -> TaskPlan:
        cleaned = normalize_space(prompt)
        detected_concepts = dedupe([*(concepts or []), *extract_concepts(cleaned, limit=8)])
        keywords = top_keywords(cleaned, limit=8)
        title = self._title(plan_type, detected_concepts, keywords)
        checklist = self._checklist(plan_type, cleaned, detected_concepts, keywords)
        estimated_days = self._estimate_days(plan_type, len(checklist))
        milestones = self._milestones(plan_type, detected_concepts, estimated_days)
        plan_resources = dedupe([*(resources or []), *self._resource_suggestions(plan_type, detected_concepts)])
        return TaskPlan(
            plan_type=plan_type,
            title=title,
            overview=self._overview(plan_type, detected_concepts),
            checklist=checklist,
            estimated_days=estimated_days,
            milestones=milestones,
            resources=plan_resources,
            metadata={
                "engine": "workspace_task_assistant_v1",
                "concepts": detected_concepts,
                "keywords": keywords,
            },
        )

    def _title(self, plan_type: ChecklistType, concepts: list[str], keywords: list[str]) -> str:
        focus = concepts[0] if concepts else keywords[0].title() if keywords else "Research"
        labels = {
            ChecklistType.RESEARCH: "Research Checklist",
            ChecklistType.LEARNING: "Learning Checklist",
            ChecklistType.IMPLEMENTATION: "Implementation Checklist",
            ChecklistType.READING: "Reading Plan",
            ChecklistType.CODING: "Coding Plan",
            ChecklistType.REVISION: "Revision Plan",
        }
        return f"{focus} {labels[plan_type]}"

    def _overview(self, plan_type: ChecklistType, concepts: list[str]) -> str:
        focus = ", ".join(concepts[:4]) if concepts else "the selected research topic"
        return f"This {plan_type.value.replace('_', ' ')} organizes the work around {focus}."

    def _checklist(
        self,
        plan_type: ChecklistType,
        prompt: str,
        concepts: list[str],
        keywords: list[str],
    ) -> list[dict[str, object]]:
        focus_terms = concepts[:5] or [keyword.title() for keyword in keywords[:5]] or ["Primary Topic"]
        templates = {
            ChecklistType.RESEARCH: [
                "Define the research question and scope",
                "Collect primary sources and implementation references",
                "Extract claims, assumptions, and evidence",
                "Compare competing approaches",
                "Summarize findings with citations",
            ],
            ChecklistType.LEARNING: [
                "Map prerequisites",
                "Study core ideas",
                "Build examples from memory",
                "Teach the concept in plain language",
                "Review weak areas",
            ],
            ChecklistType.IMPLEMENTATION: [
                "Define inputs, outputs, and constraints",
                "Design architecture and interfaces",
                "Implement the narrow core first",
                "Add validation and error handling",
                "Write tests and measure behavior",
            ],
            ChecklistType.READING: [
                "Preview abstract, introduction, and conclusion",
                "Extract terminology and definitions",
                "Annotate methods and experiments",
                "Capture open questions",
                "Create a final summary",
            ],
            ChecklistType.CODING: [
                "Inspect existing patterns",
                "Choose data structures and boundaries",
                "Implement in small verifiable steps",
                "Run static checks and tests",
                "Document interfaces",
            ],
            ChecklistType.REVISION: [
                "Identify recall targets",
                "Review summaries and flashcards",
                "Practice active recall",
                "Resolve confusing concepts",
                "Schedule spaced review",
            ],
        }
        checklist: list[dict[str, object]] = []
        for index, item in enumerate(templates[plan_type], start=1):
            concept = focus_terms[(index - 1) % len(focus_terms)]
            checklist.append(
                {
                    "order": index,
                    "title": item,
                    "description": f"{item} for {concept}.",
                    "status": "pending",
                    "priority": "high" if index <= 2 else "medium",
                    "evidence": prompt[:240],
                }
            )
        return checklist

    def _estimate_days(self, plan_type: ChecklistType, item_count: int) -> int:
        base = {
            ChecklistType.RESEARCH: 7,
            ChecklistType.LEARNING: 10,
            ChecklistType.IMPLEMENTATION: 6,
            ChecklistType.READING: 3,
            ChecklistType.CODING: 5,
            ChecklistType.REVISION: 4,
        }[plan_type]
        return max(1, base + item_count // 3)

    def _milestones(self, plan_type: ChecklistType, concepts: list[str], estimated_days: int) -> list[str]:
        focus = concepts[0] if concepts else "topic"
        return [
            f"Day 1: Frame the {focus} objective",
            f"Midpoint: Produce a working understanding of {focus}",
            f"Day {estimated_days}: Capture conclusions and next actions",
        ]

    def _resource_suggestions(self, plan_type: ChecklistType, concepts: list[str]) -> list[str]:
        focus = concepts[0] if concepts else "the topic"
        base = [f"Workspace notes related to {focus}", f"Knowledge graph neighbors for {focus}"]
        if plan_type in {ChecklistType.READING, ChecklistType.RESEARCH}:
            base.append(f"Uploaded papers and citations related to {focus}")
        if plan_type in {ChecklistType.CODING, ChecklistType.IMPLEMENTATION}:
            base.append(f"Code snippets and repositories related to {focus}")
        return base
