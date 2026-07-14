import re

from knowledge_engine.types import DifficultyLevel, KnowledgeMetadata, SourceType
from knowledge_engine.utils import content_hash, dedupe_preserve_order, title_case_phrase, words


class MetadataGenerator:
    STOPWORDS = {
        "about",
        "after",
        "also",
        "from",
        "have",
        "into",
        "more",
        "such",
        "than",
        "that",
        "their",
        "there",
        "these",
        "this",
        "through",
        "using",
        "were",
        "when",
        "where",
        "which",
        "while",
        "with",
        "would",
    }

    def generate(
        self,
        *,
        text: str,
        source_type: SourceType,
        title: str,
        author: str | None,
        requested_category: str | None,
        keywords: list[str],
    ) -> KnowledgeMetadata:
        word_values = words(text)
        word_count = len(word_values)
        topics = self._topics(text, keywords)
        category = requested_category or self._category(source_type, text, topics)
        difficulty = self._difficulty(text, word_count)
        reading_time = max(1, round(word_count / 220))
        return KnowledgeMetadata(
            title=title,
            author=author,
            category=category,
            topics=topics,
            difficulty=difficulty,
            estimated_reading_time_minutes=reading_time,
            word_count=word_count,
            character_count=len(text),
            language="en",
            content_hash=content_hash(text),
        )

    def _topics(self, text: str, keywords: list[str]) -> list[str]:
        heading_candidates = [
            re.sub(r"^\s{0,3}#{1,6}\s*", "", line).strip(": ")
            for line in text.splitlines()
            if 2 <= len(line.split()) <= 9 and not line.endswith(".")
        ]
        heading_candidates = [title_case_phrase(value) for value in heading_candidates[:10]]
        keyword_topics = [title_case_phrase(keyword) for keyword in keywords[:8]]
        return dedupe_preserve_order([*heading_candidates, *keyword_topics])[:12]

    def _category(self, source_type: SourceType, text: str, topics: list[str]) -> str:
        lower_text = text.lower()
        engineering_markers = ("api", "sdk", "database")
        if source_type == SourceType.GITHUB_REPOSITORY or any(word in lower_text for word in engineering_markers):
            return "Engineering"
        if source_type in {SourceType.RESEARCH_PAPER, SourceType.PDF} and "abstract" in lower_text:
            return "Research"
        if any(topic.lower() in {"machine learning", "deep learning", "neural network"} for topic in topics):
            return "Artificial Intelligence"
        return "Knowledge"

    def _difficulty(self, text: str, word_count: int) -> DifficultyLevel:
        word_values = [word.lower() for word in words(text)]
        unique_ratio = len(set(word_values)) / max(1, len(word_values))
        technical_markers = sum(
            1
            for marker in ("algorithm", "architecture", "theorem", "gradient", "embedding", "complexity", "proof")
            if marker in text.lower()
        )
        score = unique_ratio + min(0.5, technical_markers * 0.08) + min(0.4, word_count / 8000)
        if score > 1.1:
            return DifficultyLevel.EXPERT
        if score > 0.82:
            return DifficultyLevel.ADVANCED
        if score > 0.55:
            return DifficultyLevel.INTERMEDIATE
        return DifficultyLevel.BEGINNER
