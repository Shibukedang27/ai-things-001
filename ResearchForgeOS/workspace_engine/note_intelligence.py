from __future__ import annotations

from workspace_engine.types import NoteAnalysis, SearchableNote
from workspace_engine.utils import (
    action_items,
    dedupe,
    extract_concepts,
    fuzzy_similarity,
    generate_title,
    infer_category,
    infer_tags,
    normalize_space,
    stable_hash,
    summarize,
    token_overlap,
    top_keywords,
)


class SmartNoteEngine:
    def analyze(
        self,
        content: str,
        *,
        title: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> NoteAnalysis:
        cleaned = normalize_space(content)
        keywords = top_keywords(cleaned, limit=14)
        concepts = extract_concepts(cleaned, limit=12)
        generated_title = title.strip()[:140] if title and title.strip() else generate_title(cleaned)
        note_category = infer_category(cleaned, category)
        summary = summarize(cleaned, title=generated_title, keywords=keywords, max_sentences=3)
        note_tags = infer_tags(cleaned, keywords, concepts, explicit=tags)
        actions = action_items(cleaned)
        duplicate_key = stable_hash("note-duplicate", " ".join(top_keywords(cleaned, limit=24)))
        content_hash = stable_hash("note-content", cleaned)
        confidence = self._confidence(cleaned, keywords, concepts)
        return NoteAnalysis(
            title=generated_title,
            summary=summary,
            keywords=keywords,
            tags=note_tags,
            concepts=concepts,
            category=note_category,
            action_items=actions,
            duplicate_key=duplicate_key,
            content_hash=content_hash,
            confidence_score=confidence,
            metadata={
                "engine": "workspace_smart_note_v1",
                "word_count": len(cleaned.split()),
                "character_count": len(cleaned),
                "generated_title": title is None or not title.strip(),
            },
        )

    def improve(self, content: str, *, mode: str = "clarify") -> str:
        cleaned = normalize_space(content)
        if mode == "structure":
            return self._structured_note(cleaned)
        if mode == "actionable":
            actions = action_items(cleaned)
            action_block = "\n\nAction Items\n" + "\n".join(f"- {item}" for item in actions) if actions else ""
            return f"{self._structured_note(cleaned)}{action_block}".strip()
        return self._clarify(cleaned)

    def related_notes(
        self,
        analysis: NoteAnalysis,
        notes: list[SearchableNote],
        *,
        limit: int = 8,
    ) -> list[dict[str, object]]:
        scored: list[dict[str, object]] = []
        concept_set = {concept.casefold() for concept in analysis.concepts}
        tag_set = {tag.casefold() for tag in analysis.tags}
        keyword_text = " ".join(analysis.keywords)
        for note in notes:
            concept_hits = sorted(concept_set & {concept.casefold() for concept in note.concepts})
            tag_hits = sorted(tag_set & {tag.casefold() for tag in note.tags})
            keyword_score = token_overlap(keyword_text, " ".join(note.keywords))
            title_score = fuzzy_similarity(analysis.title, note.title)
            score = min(
                1.0,
                keyword_score * 0.45
                + title_score * 0.25
                + len(concept_hits) * 0.08
                + len(tag_hits) * 0.05,
            )
            if score <= 0.12:
                continue
            scored.append(
                {
                    "note_id": note.id,
                    "title": note.title,
                    "score": round(score, 4),
                    "shared_concepts": concept_hits,
                    "shared_tags": tag_hits,
                    "reason": self._related_reason(concept_hits, tag_hits, keyword_score, title_score),
                }
            )
        return sorted(scored, key=lambda item: (-float(item["score"]), str(item["title"])))[:limit]

    def detect_duplicate_notes(
        self,
        analysis: NoteAnalysis,
        notes: list[SearchableNote],
        *,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        duplicates: list[dict[str, object]] = []
        comparison_text = f"{analysis.title} {' '.join(analysis.keywords)} {' '.join(analysis.concepts)}"
        for note in notes:
            candidate_text = f"{note.title} {' '.join(note.keywords)} {' '.join(note.concepts)}"
            score = max(
                fuzzy_similarity(comparison_text, candidate_text),
                token_overlap(comparison_text, candidate_text),
            )
            if score >= 0.72:
                duplicates.append(
                    {
                        "note_id": note.id,
                        "title": note.title,
                        "score": round(score, 4),
                        "reason": "The note has highly similar title, keywords, or concept coverage.",
                    }
                )
        return sorted(duplicates, key=lambda item: -float(item["score"]))[:limit]

    def _confidence(self, content: str, keywords: list[str], concepts: list[str]) -> float:
        word_count = len(content.split())
        density = min(0.2, (len(keywords) + len(concepts)) / 120)
        length_score = 0.35 if word_count >= 80 else 0.2 if word_count >= 25 else 0.1
        return round(min(0.96, 0.44 + density + length_score), 4)

    def _structured_note(self, content: str) -> str:
        analysis = self.analyze(content)
        sections = [
            f"# {analysis.title}",
            f"## Summary\n{analysis.summary}",
            "## Key Ideas\n" + "\n".join(f"- {item}" for item in dedupe([*analysis.concepts, *analysis.keywords])[:10]),
        ]
        if analysis.action_items:
            sections.append("## Action Items\n" + "\n".join(f"- {item}" for item in analysis.action_items))
        return "\n\n".join(sections)

    def _clarify(self, content: str) -> str:
        text = content.strip()
        replacements = {
            "can't": "cannot",
            "won't": "will not",
            "it's": "it is",
            "that's": "that is",
            "there's": "there is",
        }
        for source, target in replacements.items():
            text = text.replace(source, target).replace(source.capitalize(), target.capitalize())
        return normalize_space(text)

    def _related_reason(
        self,
        concepts: list[str],
        tags: list[str],
        keyword_score: float,
        title_score: float,
    ) -> str:
        if concepts:
            return f"Shares concepts: {', '.join(concepts[:4])}."
        if tags:
            return f"Shares tags: {', '.join(tags[:4])}."
        if keyword_score >= title_score:
            return "Overlapping keywords indicate a related workspace note."
        return "Similar title language indicates a related workspace note."
