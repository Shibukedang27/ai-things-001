import re

from knowledge_engine.types import ConceptCandidate, DifficultyLevel, KeywordCandidate
from knowledge_engine.utils import clamp_score, dedupe_preserve_order, sentences, title_case_phrase


class ConceptExtractor:
    CONCEPT_PATTERNS = (
        re.compile(
            r"\b(?:concept|principle|architecture|algorithm|framework|method|technique)\s+of\s+"
            r"([A-Z][A-Za-z0-9 -]{2,60})"
        ),
        re.compile(r"\b([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){1,4})\b"),
    )

    def extract(self, text: str, keywords: list[KeywordCandidate], *, limit: int = 28) -> list[ConceptCandidate]:
        candidate_names: list[str] = []
        for pattern in self.CONCEPT_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1).strip(" .,:;()[]")
                if self._is_valid_name(name):
                    candidate_names.append(title_case_phrase(name))

        candidate_names.extend(title_case_phrase(keyword.value) for keyword in keywords[:18])
        names = dedupe_preserve_order(candidate_names)[:limit]
        text_sentences = sentences(text)

        concepts: list[ConceptCandidate] = []
        for index, name in enumerate(names):
            evidence_sentence = self._first_sentence_for(name, text_sentences)
            difficulty = self._difficulty(name, evidence_sentence)
            concepts.append(
                ConceptCandidate(
                    name=name,
                    description=evidence_sentence or f"{name} is a recurring idea in this knowledge source.",
                    concept_type="core" if index < 8 else "sub",
                    prerequisites=self._prerequisites(name, names),
                    dependencies=self._dependencies(name, names),
                    difficulty_level=difficulty,
                    confidence_score=clamp_score(0.92 - index * 0.018 if evidence_sentence else 0.68 - index * 0.01),
                )
            )
        return concepts

    def _is_valid_name(self, name: str) -> bool:
        words = name.split()
        if not 1 <= len(words) <= 5:
            return False
        blocked = {"The", "This", "These", "When", "Where", "Figure", "Table", "References"}
        return words[0] not in blocked and not name.isdigit()

    def _first_sentence_for(self, name: str, text_sentences: list[str]) -> str:
        lower_name = name.lower()
        for sentence in text_sentences:
            if lower_name in sentence.lower():
                return sentence[:420]
        return ""

    def _difficulty(self, name: str, evidence: str) -> DifficultyLevel:
        lower = f"{name} {evidence}".lower()
        if any(marker in lower for marker in ("proof", "theorem", "gradient", "distributed", "optimization")):
            return DifficultyLevel.ADVANCED
        if any(marker in lower for marker in ("algorithm", "architecture", "embedding", "inference", "database")):
            return DifficultyLevel.INTERMEDIATE
        return DifficultyLevel.BEGINNER

    def _prerequisites(self, name: str, names: list[str]) -> list[str]:
        lower = name.lower()
        if "neural" in lower or "embedding" in lower:
            return ["Linear Algebra", "Probability"]
        if "database" in lower or "sql" in lower:
            return ["Data Modeling"]
        return names[:2] if len(names) > 2 and name not in names[:2] else []

    def _dependencies(self, name: str, names: list[str]) -> list[str]:
        related = [candidate for candidate in names if candidate != name and candidate.lower() in name.lower()]
        return related[:3]
