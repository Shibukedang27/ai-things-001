"""Question catalog service."""

from app.domain.enums import DifficultyLevel, QuestionCategory
from app.schemas.question import DifficultyLevelRead, QuestionCategoryRead


class QuestionCatalogService:
    """Read-only service for supported question metadata."""

    def list_categories(self) -> list[QuestionCategoryRead]:
        return [
            QuestionCategoryRead(
                id=QuestionCategory.BACKGROUND,
                label="Background",
                description="Career history, motivations, and role fit.",
            ),
            QuestionCategoryRead(
                id=QuestionCategory.BEHAVIORAL,
                label="Behavioral",
                description="Past behavior, collaboration, judgment, and communication.",
            ),
            QuestionCategoryRead(
                id=QuestionCategory.TECHNICAL,
                label="Technical",
                description="Role-specific technical knowledge and problem solving.",
            ),
            QuestionCategoryRead(
                id=QuestionCategory.SYSTEM_DESIGN,
                label="System Design",
                description="Architecture, tradeoffs, scale, and reliability.",
            ),
            QuestionCategoryRead(
                id=QuestionCategory.LEADERSHIP,
                label="Leadership",
                description="Influence, ownership, conflict resolution, and decision making.",
            ),
        ]

    def list_difficulty_levels(self) -> list[DifficultyLevelRead]:
        return [
            DifficultyLevelRead(
                id=DifficultyLevel.EASY,
                label="Easy",
                description="Warm-up prompts and foundational screening questions.",
            ),
            DifficultyLevelRead(
                id=DifficultyLevel.MEDIUM,
                label="Medium",
                description="Standard interview prompts requiring structured examples.",
            ),
            DifficultyLevelRead(
                id=DifficultyLevel.HARD,
                label="Hard",
                description="Deep-dive prompts with ambiguity, edge cases, or tradeoffs.",
            ),
            DifficultyLevelRead(
                id=DifficultyLevel.EXPERT,
                label="Expert",
                description="Senior-level prompts focused on strategy, systems, and judgment.",
            ),
        ]
