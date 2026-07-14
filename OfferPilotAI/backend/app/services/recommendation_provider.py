"""Learning recommendation provider."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from statistics import mean

from app.models import AnswerEvaluation, Interview, InterviewHistory, Question
from app.schemas.recommendation import WeakTopic


@dataclass(frozen=True)
class RecommendationInput:
    """Recommendation input context."""

    target_role: str
    estimated_weeks: int
    evaluation_context: list[tuple[AnswerEvaluation, Question, Interview]]
    history: list[InterviewHistory]


@dataclass(frozen=True)
class RecommendationPlan:
    """Generated recommendation plan."""

    weak_topics: list[WeakTopic]
    recommended_topics: list[str]
    leetcode_problems: list[dict]
    hackerrank_problems: list[dict]
    books: list[dict]
    courses: list[dict]
    youtube_videos: list[dict]
    daily_practice_plan: list[dict]
    weekly_roadmap: list[dict]
    monthly_roadmap: list[dict]
    milestones: list[dict]
    source_summary: dict


class LearningRecommendationProvider:
    """Recommendation provider interface."""

    async def generate(self, payload: RecommendationInput) -> RecommendationPlan:
        raise NotImplementedError


class CatalogLearningRecommendationProvider(LearningRecommendationProvider):
    """Catalog-backed deterministic recommendation provider."""

    async def generate(self, payload: RecommendationInput) -> RecommendationPlan:
        weak_topics = self._weak_topics(payload.evaluation_context)
        if not weak_topics:
            weak_topics = self._fallback_topics(payload)

        recommended_topics = [topic.topic for topic in weak_topics]
        leetcode = self._resources("leetcode", weak_topics)
        hackerrank = self._resources("hackerrank", weak_topics)
        books = self._resources("books", weak_topics)
        courses = self._resources("courses", weak_topics)
        youtube = self._resources("youtube", weak_topics)
        daily = self._daily_plan(weak_topics)
        weekly = self._weekly_roadmap(weak_topics, payload.estimated_weeks)
        monthly = self._monthly_roadmap(weak_topics, payload.target_role)
        milestones = self._milestones(weak_topics, payload.estimated_weeks)

        return RecommendationPlan(
            weak_topics=weak_topics,
            recommended_topics=recommended_topics,
            leetcode_problems=leetcode,
            hackerrank_problems=hackerrank,
            books=books,
            courses=courses,
            youtube_videos=youtube,
            daily_practice_plan=daily,
            weekly_roadmap=weekly,
            monthly_roadmap=monthly,
            milestones=milestones,
            source_summary={
                "target_role": payload.target_role,
                "evaluations_analyzed": len(payload.evaluation_context),
                "history_events_analyzed": len(payload.history),
                "weak_topic_count": len(weak_topics),
            },
        )

    def _weak_topics(self, rows: list[tuple[AnswerEvaluation, Question, Interview]]) -> list[WeakTopic]:
        grouped: dict[str, list[tuple[AnswerEvaluation, Question]]] = {}
        for evaluation, question, _interview in rows:
            grouped.setdefault(question.category, []).append((evaluation, question))

        weak_topics: list[WeakTopic] = []
        for category, category_rows in grouped.items():
            scores = [Decimal(row[0].overall_score) for row in category_rows]
            average_score = self._decimal(mean(scores))
            weak_dimensions = self._weak_dimensions([row[0] for row in category_rows])
            if average_score < Decimal("78.00") or weak_dimensions:
                weak_topics.append(
                    WeakTopic(
                        topic=self._topic_label(category),
                        category=category,
                        priority=self._priority(average_score),
                        average_score=average_score,
                        weak_dimensions=weak_dimensions,
                        evidence_count=len(category_rows),
                    )
                )

        return sorted(weak_topics, key=lambda item: (item.average_score, -item.evidence_count))[:6]

    def _weak_dimensions(self, evaluations: list[AnswerEvaluation]) -> list[str]:
        dimensions = [
            "technical_accuracy",
            "communication",
            "completeness",
            "confidence_score",
            "problem_solving",
            "explanation_quality",
        ]
        weak: list[str] = []
        for dimension in dimensions:
            average_score = self._decimal(mean(Decimal(getattr(evaluation, dimension)) for evaluation in evaluations))
            if average_score < Decimal("75.00"):
                weak.append(dimension)
        return weak

    def _fallback_topics(self, payload: RecommendationInput) -> list[WeakTopic]:
        return [
            WeakTopic(
                topic="Interview fundamentals",
                category="behavioral",
                priority="medium",
                average_score=Decimal("70.00"),
                weak_dimensions=["communication", "completeness"],
                evidence_count=len(payload.history),
            )
        ]

    def _resources(self, resource_type: str, weak_topics: list[WeakTopic]) -> list[dict]:
        catalog = self._catalog()[resource_type]
        resources: list[dict] = []
        for topic in weak_topics:
            resources.extend(catalog.get(topic.category, catalog["default"]))
        return self._dedupe(resources)[:10]

    def _daily_plan(self, weak_topics: list[WeakTopic]) -> list[dict]:
        primary_topics = weak_topics[:3]
        plan: list[dict] = []
        for day in range(1, 8):
            topic = primary_topics[(day - 1) % len(primary_topics)]
            plan.append(
                {
                    "day": day,
                    "focus": topic.topic,
                    "duration_minutes": 75,
                    "tasks": [
                        "Review one concept note",
                        "Solve one focused practice problem",
                        "Record a 5-minute verbal explanation",
                        "Write one improvement note",
                    ],
                }
            )
        return plan

    def _weekly_roadmap(self, weak_topics: list[WeakTopic], estimated_weeks: int) -> list[dict]:
        roadmap: list[dict] = []
        for week in range(1, min(estimated_weeks, 12) + 1):
            topic = weak_topics[(week - 1) % len(weak_topics)]
            roadmap.append(
                {
                    "week": week,
                    "theme": topic.topic,
                    "goal": f"Raise {topic.topic} performance above 80%.",
                    "deliverables": [
                        "Complete 5 practice problems",
                        "Review 2 reference resources",
                        "Run 1 timed mock interview segment",
                    ],
                }
            )
        return roadmap

    def _monthly_roadmap(self, weak_topics: list[WeakTopic], target_role: str) -> list[dict]:
        themes = ["Foundation repair", "Timed practice", "Interview simulation"]
        return [
            {
                "month": index + 1,
                "theme": theme,
                "target_role": target_role,
                "focus_topics": [topic.topic for topic in weak_topics[index::3]] or [weak_topics[0].topic],
                "outcome": "Measurable improvement in answer quality and consistency.",
            }
            for index, theme in enumerate(themes)
        ]

    def _milestones(self, weak_topics: list[WeakTopic], estimated_weeks: int) -> list[dict]:
        return [
            {
                "milestone": "Baseline review",
                "week": 1,
                "success_metric": "Explain every weak topic in under 3 minutes.",
            },
            {
                "milestone": "Practice volume",
                "week": max(2, estimated_weeks // 2),
                "success_metric": "Complete recommended problem sets with written reflections.",
            },
            {
                "milestone": "Mock readiness",
                "week": estimated_weeks,
                "success_metric": f"Score 80+ on {', '.join(topic.topic for topic in weak_topics[:3])}.",
            },
        ]

    def _priority(self, average_score: Decimal) -> str:
        if average_score < Decimal("60.00"):
            return "high"
        if average_score < Decimal("75.00"):
            return "medium"
        return "low"

    def _topic_label(self, category: str) -> str:
        return category.replace("_", " ").title()

    def _decimal(self, value) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _dedupe(self, resources: list[dict]) -> list[dict]:
        seen: set[str] = set()
        deduped: list[dict] = []
        for resource in resources:
            key = f"{resource.get('platform')}::{resource.get('title')}"
            if key in seen:
                continue
            seen.add(key)
            deduped.append(resource)
        return deduped

    def _catalog(self) -> dict[str, dict[str, list[dict]]]:
        return {
            "leetcode": {
                "python": [{"platform": "LeetCode", "title": "Top K Frequent Elements", "difficulty": "Medium"}],
                "java": [{"platform": "LeetCode", "title": "LRU Cache", "difficulty": "Medium"}],
                "sql": [{"platform": "LeetCode", "title": "Second Highest Salary", "difficulty": "Medium"}],
                "dsa": [{"platform": "LeetCode", "title": "Merge Intervals", "difficulty": "Medium"}],
                "system_design": [{"platform": "LeetCode", "title": "Design Twitter", "difficulty": "Medium"}],
                "machine_learning": [{"platform": "LeetCode", "title": "Sparse Matrix Multiplication", "difficulty": "Medium"}],
                "deep_learning": [{"platform": "LeetCode", "title": "Matrix Block Sum", "difficulty": "Medium"}],
                "nlp": [{"platform": "LeetCode", "title": "Word Break", "difficulty": "Medium"}],
                "prompt_engineering": [{"platform": "LeetCode", "title": "Text Justification", "difficulty": "Hard"}],
                "behavioral": [{"platform": "LeetCode", "title": "Design Add and Search Words Data Structure", "difficulty": "Medium"}],
                "hr": [{"platform": "LeetCode", "title": "Valid Anagram", "difficulty": "Easy"}],
                "default": [{"platform": "LeetCode", "title": "Two Sum", "difficulty": "Easy"}],
            },
            "hackerrank": {
                "python": [{"platform": "HackerRank", "title": "Python Collections", "difficulty": "Medium"}],
                "java": [{"platform": "HackerRank", "title": "Java Generics", "difficulty": "Medium"}],
                "sql": [{"platform": "HackerRank", "title": "SQL Advanced Select", "difficulty": "Medium"}],
                "dsa": [{"platform": "HackerRank", "title": "Data Structures: Heaps", "difficulty": "Medium"}],
                "system_design": [{"platform": "HackerRank", "title": "REST API Intermediate", "difficulty": "Medium"}],
                "machine_learning": [{"platform": "HackerRank", "title": "Statistics and Machine Learning", "difficulty": "Medium"}],
                "deep_learning": [{"platform": "HackerRank", "title": "Linear Algebra Foundations", "difficulty": "Medium"}],
                "nlp": [{"platform": "HackerRank", "title": "Text Processing", "difficulty": "Medium"}],
                "prompt_engineering": [{"platform": "HackerRank", "title": "Regex and Parsing", "difficulty": "Medium"}],
                "behavioral": [{"platform": "HackerRank", "title": "Problem Solving Basic", "difficulty": "Easy"}],
                "hr": [{"platform": "HackerRank", "title": "Communication Practice Prompts", "difficulty": "Easy"}],
                "default": [{"platform": "HackerRank", "title": "Problem Solving Warmup", "difficulty": "Easy"}],
            },
            "books": {
                "python": [{"platform": "Book", "title": "Fluent Python", "author": "Luciano Ramalho"}],
                "java": [{"platform": "Book", "title": "Effective Java", "author": "Joshua Bloch"}],
                "sql": [{"platform": "Book", "title": "SQL Performance Explained", "author": "Markus Winand"}],
                "dsa": [{"platform": "Book", "title": "Cracking the Coding Interview", "author": "Gayle Laakmann McDowell"}],
                "system_design": [{"platform": "Book", "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann"}],
                "machine_learning": [{"platform": "Book", "title": "Hands-On Machine Learning", "author": "Aurelien Geron"}],
                "deep_learning": [{"platform": "Book", "title": "Deep Learning", "author": "Goodfellow, Bengio, Courville"}],
                "nlp": [{"platform": "Book", "title": "Speech and Language Processing", "author": "Jurafsky and Martin"}],
                "prompt_engineering": [{"platform": "Book", "title": "Prompt Engineering for Generative AI", "author": "James Phoenix and Mike Taylor"}],
                "behavioral": [{"platform": "Book", "title": "The STAR Interview Method", "author": "Misha Yurchenko"}],
                "hr": [{"platform": "Book", "title": "The 2-Hour Job Search", "author": "Steve Dalton"}],
                "default": [{"platform": "Book", "title": "The Pragmatic Programmer", "author": "Hunt and Thomas"}],
            },
            "courses": {
                "python": [{"platform": "Course", "title": "Advanced Python Programming"}],
                "java": [{"platform": "Course", "title": "Java Concurrency and Performance"}],
                "sql": [{"platform": "Course", "title": "Advanced SQL for Data Engineering"}],
                "dsa": [{"platform": "Course", "title": "Algorithms Specialization"}],
                "system_design": [{"platform": "Course", "title": "System Design Interview Prep"}],
                "machine_learning": [{"platform": "Course", "title": "Machine Learning Specialization"}],
                "deep_learning": [{"platform": "Course", "title": "Deep Learning Specialization"}],
                "nlp": [{"platform": "Course", "title": "Natural Language Processing Specialization"}],
                "prompt_engineering": [{"platform": "Course", "title": "Prompt Engineering for Developers"}],
                "behavioral": [{"platform": "Course", "title": "Behavioral Interview Preparation"}],
                "hr": [{"platform": "Course", "title": "Interview Communication and Negotiation"}],
                "default": [{"platform": "Course", "title": "Technical Interview Foundations"}],
            },
            "youtube": {
                "python": [{"platform": "YouTube", "title": "Python Interview Patterns"}],
                "java": [{"platform": "YouTube", "title": "Java Interview Deep Dive"}],
                "sql": [{"platform": "YouTube", "title": "SQL Query Optimization Explained"}],
                "dsa": [{"platform": "YouTube", "title": "Data Structures and Algorithms Roadmap"}],
                "system_design": [{"platform": "YouTube", "title": "System Design Interview Fundamentals"}],
                "machine_learning": [{"platform": "YouTube", "title": "Machine Learning Interview Questions"}],
                "deep_learning": [{"platform": "YouTube", "title": "Deep Learning Concepts for Interviews"}],
                "nlp": [{"platform": "YouTube", "title": "NLP Interview Preparation"}],
                "prompt_engineering": [{"platform": "YouTube", "title": "Prompt Engineering Best Practices"}],
                "behavioral": [{"platform": "YouTube", "title": "STAR Method Interview Answers"}],
                "hr": [{"platform": "YouTube", "title": "HR Interview Questions and Answers"}],
                "default": [{"platform": "YouTube", "title": "Technical Interview Preparation Plan"}],
            },
        }
