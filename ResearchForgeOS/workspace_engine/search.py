from __future__ import annotations

from datetime import date

from retrieval.embedding import RetrievalEmbeddingService
from retrieval.utils import cosine_similarity

from workspace_engine.types import NoteSearchResult, SearchableNote, SearchMode
from workspace_engine.utils import fuzzy_similarity, normalize_space, token_overlap, tokenize


class WorkspaceSearchEngine:
    def __init__(self, embedding_service: RetrievalEmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or RetrievalEmbeddingService()

    def search(
        self,
        query: str,
        notes: list[SearchableNote],
        *,
        mode: SearchMode = SearchMode.HYBRID,
        tags: list[str] | None = None,
        project_id: str | None = None,
        collection_id: str | None = None,
        author: str | None = None,
        concepts: list[str] | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 25,
    ) -> list[NoteSearchResult]:
        cleaned_query = normalize_space(query)
        filtered = self._filter_notes(
            notes,
            tags=tags or [],
            project_id=project_id,
            collection_id=collection_id,
            author=author,
            concepts=concepts or [],
            date_from=date_from,
            date_to=date_to,
        )
        query_vector = self.embedding_service.embed_text(cleaned_query) if cleaned_query else []
        results = [
            self._score_note(note, cleaned_query, query_vector, mode)
            for note in filtered
        ]
        scored = [result for result in results if result.score > 0 or not cleaned_query]
        return sorted(scored, key=lambda item: (-item.score, item.title))[:limit]

    def _filter_notes(
        self,
        notes: list[SearchableNote],
        *,
        tags: list[str],
        project_id: str | None,
        collection_id: str | None,
        author: str | None,
        concepts: list[str],
        date_from: date | None,
        date_to: date | None,
    ) -> list[SearchableNote]:
        normalized_tags = {tag.casefold() for tag in tags}
        normalized_concepts = {concept.casefold() for concept in concepts}
        output: list[SearchableNote] = []
        for note in notes:
            if project_id and note.project_id != project_id:
                continue
            if collection_id and note.collection_id != collection_id:
                continue
            if author and (note.author or "").casefold() != author.casefold():
                continue
            if normalized_tags and not normalized_tags <= {tag.casefold() for tag in note.tags}:
                continue
            if normalized_concepts and not normalized_concepts & {concept.casefold() for concept in note.concepts}:
                continue
            created_date = note.created_at.date() if note.created_at else None
            if date_from and (created_date is None or created_date < date_from):
                continue
            if date_to and (created_date is None or created_date > date_to):
                continue
            output.append(note)
        return output

    def _score_note(
        self,
        note: SearchableNote,
        query: str,
        query_vector: list[float],
        mode: SearchMode,
    ) -> NoteSearchResult:
        search_blob = " ".join(
            [
                note.title,
                note.summary,
                note.content,
                " ".join(note.tags),
                " ".join(note.keywords),
                " ".join(note.concepts),
                note.category,
            ]
        )
        matched_fields: list[str] = []
        keyword_score = token_overlap(query, search_blob) if query else 0.0
        fuzzy_score = max(fuzzy_similarity(query, note.title), fuzzy_similarity(query, note.summary)) if query else 0.0
        tag_score = token_overlap(query, " ".join(note.tags)) if query else 0.0
        concept_score = token_overlap(query, " ".join(note.concepts)) if query else 0.0
        semantic_score = (
            cosine_similarity(query_vector, note.embedding)
            if query_vector and note.embedding
            else self._fallback_semantic(query, search_blob)
        )
        if keyword_score:
            matched_fields.append("content")
        if fuzzy_score > 0.35:
            matched_fields.append("title")
        if tag_score:
            matched_fields.append("tags")
        if concept_score:
            matched_fields.append("concepts")
        if semantic_score > 0.2:
            matched_fields.append("semantic")
        score_lookup = {
            SearchMode.SEMANTIC: semantic_score,
            SearchMode.KEYWORD: keyword_score,
            SearchMode.FUZZY: fuzzy_score,
            SearchMode.TAG: tag_score,
            SearchMode.CONCEPT: concept_score,
            SearchMode.PROJECT: 1.0,
            SearchMode.AUTHOR: 1.0,
            SearchMode.DATE: 1.0,
        }
        if mode == SearchMode.HYBRID:
            score = (
                semantic_score * 0.34
                + keyword_score * 0.24
                + fuzzy_score * 0.18
                + tag_score * 0.12
                + concept_score * 0.12
            )
        else:
            score = score_lookup.get(mode, keyword_score)
        return NoteSearchResult(
            note_id=note.id,
            title=note.title,
            summary=note.summary,
            score=round(min(1.0, score), 4),
            matched_fields=sorted(set(matched_fields)),
            tags=note.tags,
            concepts=note.concepts,
            project_id=note.project_id,
            collection_id=note.collection_id,
        )

    def _fallback_semantic(self, query: str, content: str) -> float:
        if not query:
            return 0.0
        query_terms = set(tokenize(query))
        content_terms = set(tokenize(content))
        if not query_terms or not content_terms:
            return 0.0
        coverage = len(query_terms & content_terms) / len(query_terms)
        density = len(query_terms & content_terms) / max(1, len(content_terms))
        return round(min(1.0, coverage * 0.8 + density * 0.2), 4)
