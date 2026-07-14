from knowledge_engine.types import SummaryBundle
from knowledge_engine.utils import sentences


class SummaryGenerator:
    def generate(self, text: str, *, title: str, keywords: list[str]) -> SummaryBundle:
        ranked = self._rank_sentences(text, keywords)
        if not ranked:
            fallback = (
                f"{title} contains knowledge material that can be organized into concepts, summaries, "
                "and learning assets."
            )
            return SummaryBundle(fallback, fallback, fallback, fallback, fallback, fallback)

        return SummaryBundle(
            executive_summary=self._join(ranked, 4),
            beginner_summary=self._beginner_summary(title, ranked, keywords),
            technical_summary=self._technical_summary(ranked, keywords),
            detailed_summary=self._join(ranked, 12),
            one_minute_summary=self._join(ranked, 3),
            five_minute_summary=self._join(ranked, 8),
        )

    def _rank_sentences(self, text: str, keywords: list[str]) -> list[str]:
        text_sentences = sentences(text)
        if not text_sentences:
            return []
        keyword_set = {keyword.lower() for keyword in keywords[:20]}
        scored: list[tuple[float, int, str]] = []
        for index, sentence in enumerate(text_sentences):
            lower = sentence.lower()
            keyword_hits = sum(1 for keyword in keyword_set if keyword in lower)
            structure_markers = ("therefore", "because", "key", "important", "result")
            structure_bonus = 1 if any(marker in lower for marker in structure_markers) else 0
            score = keyword_hits * 2 + structure_bonus + max(0, 3 - index * 0.05)
            scored.append((score, index, sentence))
        selected = sorted(scored, key=lambda item: (-item[0], item[1]))
        return [sentence for _, _, sentence in selected]

    def _join(self, ranked: list[str], count: int) -> str:
        selected = ranked[:count]
        ordered = sorted(selected, key=lambda sentence: ranked.index(sentence))
        return " ".join(ordered).strip()

    def _beginner_summary(self, title: str, ranked: list[str], keywords: list[str]) -> str:
        opening = f"{title} is best understood through its main ideas"
        if keywords:
            opening += f": {', '.join(keywords[:5])}."
        else:
            opening += "."
        return f"{opening} {self._join(ranked, 4)}"

    def _technical_summary(self, ranked: list[str], keywords: list[str]) -> str:
        context = self._join(ranked, 5)
        if keywords:
            return f"Technical focus areas include {', '.join(keywords[:8])}. {context}"
        return context
