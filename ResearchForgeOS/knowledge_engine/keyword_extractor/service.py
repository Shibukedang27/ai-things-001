from collections import Counter

from knowledge_engine.types import KeywordCandidate
from knowledge_engine.utils import clamp_score, words


class KeywordExtractor:
    STOPWORDS = {
        "able",
        "about",
        "above",
        "across",
        "after",
        "again",
        "against",
        "algorithm",
        "because",
        "before",
        "being",
        "between",
        "could",
        "document",
        "during",
        "every",
        "first",
        "found",
        "from",
        "having",
        "important",
        "inside",
        "large",
        "learn",
        "method",
        "model",
        "other",
        "paper",
        "research",
        "should",
        "system",
        "their",
        "there",
        "these",
        "thing",
        "those",
        "through",
        "under",
        "using",
        "where",
        "which",
        "while",
        "would",
    }

    def extract(self, text: str, *, limit: int = 32) -> list[KeywordCandidate]:
        normalized_words = [word.lower() for word in words(text) if len(word) > 3]
        filtered = [word for word in normalized_words if word not in self.STOPWORDS and not word.isdigit()]
        single_counts = Counter(filtered)
        bigram_counts = Counter(zip(filtered, filtered[1:], strict=False))

        candidates: dict[str, tuple[int, float]] = {}
        for word, count in single_counts.most_common(limit * 2):
            candidates[word] = (count, count)
        for (left, right), count in bigram_counts.most_common(limit):
            if left != right and count > 1:
                phrase = f"{left} {right}"
                candidates[phrase] = (count, count * 1.8)

        if not candidates:
            return []

        max_score = max(score for _, score in candidates.values())
        ranked = sorted(candidates.items(), key=lambda item: (-item[1][1], item[0]))[:limit]
        return [
            KeywordCandidate(value=value, occurrence_count=count, relevance_score=clamp_score(score / max_score))
            for value, (count, score) in ranked
        ]
