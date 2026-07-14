from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from retrieval import HybridKnowledgeRetrievalEngine
from retrieval.embedding import RetrievalEmbeddingService
from retrieval.types import (
    Citation,
    KnowledgeSection,
    QueryProfile,
    ReasonedAnswer,
    ReasoningStep,
    RetrievalCandidate,
    SearchMode,
    SearchOptions,
)
from retrieval.utils import stable_hash
from sqlalchemy.orm import Session

from backend.config.settings import get_settings
from backend.exceptions import NotFoundError, ValidationError
from backend.models.document import Document
from backend.models.retrieval import CitationHistory, KnowledgeCache, ReasoningLog, RetrievalHistory, RetrievalQuery
from backend.models.user import User
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.retrieval_repository import (
    CitationHistoryRepository,
    KnowledgeCacheRepository,
    RetrievalEmbeddingRepository,
    RetrievalHistoryRepository,
    RetrievalQueryRepository,
)
from backend.schemas.retrieval import (
    AskQuestionRequest,
    CitationRead,
    CitationViewerResponse,
    ReasoningHistoryItem,
    ReasoningStepRead,
    RelatedConceptRead,
    RelatedConceptsResponse,
    RetrievalAnswerRead,
    RetrievalRequest,
    RetrievedSectionRead,
    SearchResponse,
)


class RetrievalService:
    def __init__(
        self,
        session: Session,
        engine: HybridKnowledgeRetrievalEngine | None = None,
        embedding_service: RetrievalEmbeddingService | None = None,
    ) -> None:
        self.session = session
        self.engine = engine or HybridKnowledgeRetrievalEngine()
        self.embedding_service = embedding_service or RetrievalEmbeddingService()
        self.documents = DocumentRepository(session)
        self.embeddings = RetrievalEmbeddingRepository(session)
        self.queries = RetrievalQueryRepository(session)
        self.histories = RetrievalHistoryRepository(session)
        self.cache = KnowledgeCacheRepository(session)
        self.citations = CitationHistoryRepository(session)
        self.settings = get_settings()

    def ask_question(self, payload: AskQuestionRequest, current_user: User) -> RetrievalAnswerRead:
        profile = self.engine.understand(payload.query, filters=payload.filters)
        options = self._options(payload)
        cache_key = stable_hash(
            "ask",
            profile.normalized_query,
            profile.intent.value,
            profile.filters,
            options.top_k,
            options.namespace,
            options.collection_name,
        )
        cached = self.cache.get_by_key(cache_key) if payload.use_cache else None
        if cached is not None:
            cached.hit_count += 1
            answer = self._answer_from_cache(cached.payload, cache_key=cache_key)
            answer = ReasonedAnswer(
                answer=answer.answer,
                confidence_score=answer.confidence_score,
                citations=answer.citations,
                retrieved_sections=answer.retrieved_sections,
                reasoning_path=answer.reasoning_path,
                supporting_evidence=answer.supporting_evidence,
                validation=answer.validation,
                cache_key=cache_key,
                cache_hit=True,
            )
        else:
            sections, vectors = self._knowledge_space(options)
            answer = self.engine.answer(profile, sections, vectors, options=options)
            self._store_cache(cache_key, profile, answer)

        query, history = self._persist_answer(profile, answer, current_user, mode=SearchMode.HYBRID.value)
        self.session.commit()
        return self._answer_read(query, history)

    def search(self, payload: RetrievalRequest, current_user: User, *, mode: SearchMode) -> SearchResponse:
        profile = self.engine.understand(payload.query, filters=payload.filters)
        options = self._options(payload)
        sections, vectors = self._knowledge_space(options)
        candidates = self.engine.search(profile, sections, vectors, mode=mode, options=options)
        query, history = self._persist_search(profile, candidates, current_user, mode=mode.value)
        self.session.commit()
        return SearchResponse(
            query_id=query.id,
            history_id=history.id,
            mode=mode.value,
            intent=profile.intent.value,
            results=[self._section_read(candidate) for candidate in candidates],
        )

    def related_concepts(self, payload: RetrievalRequest, current_user: User) -> RelatedConceptsResponse:
        profile = self.engine.understand(payload.query, filters=payload.filters)
        options = self._options(payload)
        sections, vectors = self._knowledge_space(options)
        candidates = self.engine.search(profile, sections, vectors, mode=SearchMode.HYBRID, options=options)
        concept_scores: dict[str, tuple[float, set[str], set[str]]] = {}
        for candidate in candidates:
            for concept in [*candidate.section.topics, *candidate.section.keywords, *candidate.section.technologies]:
                normalized = concept.strip()
                if not normalized:
                    continue
                score, document_ids, titles = concept_scores.get(normalized, (0.0, set(), set()))
                document_ids.add(candidate.section.document_id)
                titles.add(candidate.section.document_title)
                concept_scores[normalized] = (max(score, candidate.score), document_ids, titles)

        query, _history = self._persist_search(profile, candidates, current_user, mode="related_concepts")
        self.session.commit()
        concepts = [
            RelatedConceptRead(
                concept=concept,
                document_ids=sorted(document_ids),
                source_titles=sorted(titles),
                relevance_score=round(score, 4),
            )
            for concept, (score, document_ids, titles) in sorted(
                concept_scores.items(),
                key=lambda item: item[1][0],
                reverse=True,
            )[: payload.top_k]
        ]
        return RelatedConceptsResponse(query_id=query.id, concepts=concepts)

    def reasoning_history(self, *, offset: int, limit: int) -> list[ReasoningHistoryItem]:
        return [
            ReasoningHistoryItem(
                id=history.id,
                query_id=history.query_id,
                query_text=history.query.query_text,
                intent=history.query.intent,
                mode=history.mode,
                status=history.status,
                answer=history.answer,
                confidence_score=history.confidence_score,
                cache_hit=history.cache_hit,
                source_documents=history.source_documents,
                created_at=history.created_at,
                updated_at=history.updated_at,
            )
            for history in self.histories.list_history(offset=offset, limit=limit)
        ]

    def citation_viewer(self, history_id: str) -> CitationViewerResponse:
        history = self.histories.get_full(history_id)
        if history is None:
            raise NotFoundError("Retrieval history was not found.")
        return CitationViewerResponse(
            history_id=history.id,
            citations=[
                self._citation_history_read(citation)
                for citation in self.citations.list_by_history(history.id)
            ],
            generated_at=datetime.now(UTC),
        )

    def _knowledge_space(self, options: SearchOptions) -> tuple[list[KnowledgeSection], dict[str, list[float]]]:
        documents = [
            full_document
            for document in self.documents.list_documents(offset=0, limit=10_000)
            if (full_document := self.documents.get_full(document.id)) is not None
        ]
        sections = [section for document in documents for section in self._sections_from_document(document)]
        vectors = {
            self._section_id(embedding.document_id, embedding.chunk_id): embedding.vector
            for embedding in self.embeddings.list_by_namespace(
                namespace=options.namespace,
                collection_name=options.collection_name,
            )
        }
        for section in sections:
            vectors.setdefault(section.section_id, self.embedding_service.embed_text(section.content))
        return sections, vectors

    def _sections_from_document(self, document: Document) -> list[KnowledgeSection]:
        keywords = [keyword.value for keyword in document.keywords]
        technologies = [technology.name for technology in document.technologies]
        sections = [
            KnowledgeSection(
                section_id=self._section_id(document.id, chunk.id),
                document_id=document.id,
                document_title=document.title,
                chunk_id=chunk.id,
                content=chunk.content,
                section_label=f"chunk-{chunk.chunk_index}",
                source_type=document.source_type,
                source_url=document.source_url,
                category=document.category,
                topics=document.topics,
                keywords=keywords,
                technologies=technologies,
                metadata={
                    "document_id": document.id,
                    "chunk_id": chunk.id,
                    "title": document.title,
                    "category": document.category,
                    "source_type": document.source_type,
                    "difficulty": document.difficulty,
                },
            )
            for chunk in sorted(document.chunks, key=lambda item: item.chunk_index)
        ]
        if sections:
            return sections
        return [
            KnowledgeSection(
                section_id=self._section_id(document.id, None),
                document_id=document.id,
                document_title=document.title,
                chunk_id=None,
                content=document.cleaned_text,
                section_label="document",
                source_type=document.source_type,
                source_url=document.source_url,
                category=document.category,
                topics=document.topics,
                keywords=keywords,
                technologies=technologies,
                metadata={
                    "document_id": document.id,
                    "title": document.title,
                    "category": document.category,
                    "source_type": document.source_type,
                    "difficulty": document.difficulty,
                },
            )
        ]

    def _persist_answer(
        self,
        profile: QueryProfile,
        answer: ReasonedAnswer,
        current_user: User,
        *,
        mode: str,
    ) -> tuple[RetrievalQuery, RetrievalHistory]:
        query = self._query_model(profile, current_user)
        self.queries.add(query)
        history = RetrievalHistory(
            query_id=query.id,
            mode=mode,
            status="completed",
            answer=answer.answer,
            confidence_score=answer.confidence_score,
            cache_hit=answer.cache_hit,
            source_documents=self._source_documents(answer.retrieved_sections),
            retrieved_sections=[self._section_payload(candidate) for candidate in answer.retrieved_sections],
            reasoning_path=[self._reasoning_payload(step) for step in answer.reasoning_path],
            supporting_evidence=answer.supporting_evidence,
            validation=answer.validation,
            metadata_json={"cache_key": answer.cache_key},
        )
        self.histories.add(history)
        self._persist_reasoning_logs(history.id, answer.reasoning_path)
        self._persist_citations(history.id, answer.citations)
        return query, history

    def _persist_search(
        self,
        profile: QueryProfile,
        candidates: list[RetrievalCandidate],
        current_user: User,
        *,
        mode: str,
    ) -> tuple[RetrievalQuery, RetrievalHistory]:
        query = self._query_model(profile, current_user)
        self.queries.add(query)
        history = RetrievalHistory(
            query_id=query.id,
            mode=mode,
            status="completed",
            answer="Search results generated.",
            confidence_score=round(sum(candidate.score for candidate in candidates) / max(1, len(candidates)), 4),
            cache_hit=False,
            source_documents=self._source_documents(candidates),
            retrieved_sections=[self._section_payload(candidate) for candidate in candidates],
            reasoning_path=[],
            supporting_evidence=[],
            validation={"result_count": len(candidates)},
            metadata_json={},
        )
        self.histories.add(history)
        return query, history

    def _query_model(self, profile: QueryProfile, current_user: User) -> RetrievalQuery:
        return RetrievalQuery(
            query_text=profile.sanitized_query,
            normalized_query=profile.normalized_query[:500],
            query_hash=stable_hash(profile.normalized_query),
            intent=profile.intent.value,
            expanded_queries=profile.expanded_queries,
            filters=profile.filters,
            requested_by_user_id=current_user.id,
        )

    def _persist_reasoning_logs(self, history_id: str, steps: list[ReasoningStep]) -> None:
        for step in steps:
            self.session.add(
                ReasoningLog(
                    retrieval_history_id=history_id,
                    step_index=step.step_index,
                    step_type=step.step_type,
                    description=step.description,
                    evidence=step.evidence,
                    confidence_score=step.confidence_score,
                )
            )

    def _persist_citations(self, history_id: str, citations: list[Citation]) -> None:
        for citation in citations:
            self.session.add(
                CitationHistory(
                    retrieval_history_id=history_id,
                    document_id=citation.document_id,
                    chunk_id=citation.chunk_id,
                    citation_key=citation.citation_key,
                    title=citation.document_title,
                    snippet=citation.snippet,
                    source_url=citation.source_url,
                    section_label=citation.section_label,
                    relevance_score=citation.relevance_score,
                    metadata_json={},
                )
            )

    def _store_cache(self, cache_key: str, profile: QueryProfile, answer: ReasonedAnswer) -> None:
        existing = self.cache.get_by_key(cache_key)
        payload = self._answer_cache_payload(answer)
        if existing is None:
            self.cache.add(
                KnowledgeCache(
                    cache_key=cache_key,
                    cache_type="retrieval_answer",
                    query_hash=stable_hash(profile.normalized_query),
                    payload=payload,
                    expires_at=None,
                    hit_count=0,
                    metadata_json={"intent": profile.intent.value},
                )
            )
        else:
            existing.payload = payload
            existing.metadata_json = {"intent": profile.intent.value}

    def _answer_from_cache(self, payload: dict[str, object], *, cache_key: str) -> ReasonedAnswer:
        return ReasonedAnswer(
            answer=str(payload.get("answer", "")),
            confidence_score=float(payload.get("confidence_score", 0.0)),
            citations=[
                Citation(
                    citation_key=str(item["citation_key"]),
                    document_id=str(item["document_id"]),
                    document_title=str(item["document_title"]),
                    chunk_id=item.get("chunk_id"),
                    snippet=str(item["snippet"]),
                    source_url=item.get("source_url"),
                    section_label=item.get("section_label"),
                    relevance_score=float(item["relevance_score"]),
                )
                for item in payload.get("citations", [])
                if isinstance(item, dict)
            ],
            retrieved_sections=[
                self._candidate_from_payload(item)
                for item in payload.get("retrieved_sections", [])
                if isinstance(item, dict)
            ],
            reasoning_path=[
                ReasoningStep(
                    step_index=int(item["step_index"]),
                    step_type=str(item["step_type"]),
                    description=str(item["description"]),
                    evidence=[str(evidence) for evidence in item.get("evidence", [])],
                    confidence_score=float(item["confidence_score"]),
                )
                for item in payload.get("reasoning_path", [])
                if isinstance(item, dict)
            ],
            supporting_evidence=[str(item) for item in payload.get("supporting_evidence", [])],
            validation=dict(payload.get("validation", {})),
            cache_key=cache_key,
            cache_hit=True,
        )

    def _candidate_from_payload(self, item: dict[str, object]) -> RetrievalCandidate:
        section = KnowledgeSection(
            section_id=str(item.get("section_id", "")),
            document_id=str(item["document_id"]),
            document_title=str(item["document_title"]),
            chunk_id=item.get("chunk_id"),
            content=str(item["content"]),
            section_label=str(item["section_label"]),
            source_type=item.get("source_type"),
            source_url=item.get("source_url"),
            topics=[str(value) for value in item.get("topics", [])],
            keywords=[str(value) for value in item.get("keywords", [])],
            technologies=[str(value) for value in item.get("technologies", [])],
            metadata=dict(item.get("metadata", {})),
        )
        return RetrievalCandidate(
            section=section,
            score=float(item["score"]),
            keyword_score=float(item["keyword_score"]),
            semantic_score=float(item["semantic_score"]),
            metadata_score=float(item["metadata_score"]),
            reasons=[str(value) for value in item.get("reasons", [])],
        )

    def _answer_cache_payload(self, answer: ReasonedAnswer) -> dict[str, object]:
        return {
            "answer": answer.answer,
            "confidence_score": answer.confidence_score,
            "citations": [
                {
                    "citation_key": citation.citation_key,
                    "document_id": citation.document_id,
                    "document_title": citation.document_title,
                    "chunk_id": citation.chunk_id,
                    "snippet": citation.snippet,
                    "source_url": citation.source_url,
                    "section_label": citation.section_label,
                    "relevance_score": citation.relevance_score,
                }
                for citation in answer.citations
            ],
            "retrieved_sections": [self._section_payload(candidate) for candidate in answer.retrieved_sections],
            "reasoning_path": [self._reasoning_payload(step) for step in answer.reasoning_path],
            "supporting_evidence": answer.supporting_evidence,
            "validation": answer.validation,
        }

    def _options(self, payload: RetrievalRequest) -> SearchOptions:
        namespace = payload.namespace or self.settings.retrieval_namespace
        collection_name = payload.collection_name or self.settings.retrieval_collection_name
        if not namespace.strip() or not collection_name.strip():
            raise ValidationError("Namespace and collection name must be provided.")
        return SearchOptions(
            top_k=payload.top_k,
            namespace=namespace,
            collection_name=collection_name,
            filters=payload.filters,
            max_context_characters=payload.max_context_characters,
        )

    def _answer_read(self, query: RetrievalQuery, history: RetrievalHistory) -> RetrievalAnswerRead:
        return RetrievalAnswerRead(
            query_id=query.id,
            history_id=history.id,
            intent=query.intent,
            answer=history.answer,
            confidence_score=history.confidence_score,
            source_documents=history.source_documents,
            citations=[
                self._citation_history_read(citation)
                for citation in self.citations.list_by_history(history.id)
            ],
            retrieved_sections=[
                self._section_read(self._candidate_from_payload(item)) for item in history.retrieved_sections
            ],
            reasoning_path=[
                ReasoningStepRead(
                    step_index=item["step_index"],
                    step_type=item["step_type"],
                    description=item["description"],
                    evidence=item["evidence"],
                    confidence_score=item["confidence_score"],
                )
                for item in history.reasoning_path
            ],
            supporting_evidence=history.supporting_evidence,
            validation=history.validation,
            cache_hit=history.cache_hit,
        )

    def _source_documents(self, candidates: list[RetrievalCandidate]) -> list[dict[str, Any]]:
        documents: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            documents.setdefault(
                candidate.section.document_id,
                {
                    "document_id": candidate.section.document_id,
                    "title": candidate.section.document_title,
                    "source_type": candidate.section.source_type,
                    "source_url": candidate.section.source_url,
                    "best_score": candidate.score,
                },
            )
            documents[candidate.section.document_id]["best_score"] = max(
                float(documents[candidate.section.document_id]["best_score"]),
                candidate.score,
            )
        return list(documents.values())

    def _section_payload(self, candidate: RetrievalCandidate) -> dict[str, Any]:
        return {
            "section_id": candidate.section.section_id,
            "document_id": candidate.section.document_id,
            "document_title": candidate.section.document_title,
            "chunk_id": candidate.section.chunk_id,
            "section_label": candidate.section.section_label,
            "content": candidate.section.content,
            "score": candidate.score,
            "keyword_score": candidate.keyword_score,
            "semantic_score": candidate.semantic_score,
            "metadata_score": candidate.metadata_score,
            "reasons": candidate.reasons,
            "source_type": candidate.section.source_type,
            "source_url": candidate.section.source_url,
            "topics": candidate.section.topics,
            "keywords": candidate.section.keywords,
            "technologies": candidate.section.technologies,
            "metadata": candidate.section.metadata,
        }

    def _reasoning_payload(self, step: ReasoningStep) -> dict[str, Any]:
        return {
            "step_index": step.step_index,
            "step_type": step.step_type,
            "description": step.description,
            "evidence": step.evidence,
            "confidence_score": step.confidence_score,
        }

    def _section_read(self, candidate: RetrievalCandidate) -> RetrievedSectionRead:
        return RetrievedSectionRead(
            document_id=candidate.section.document_id,
            document_title=candidate.section.document_title,
            chunk_id=candidate.section.chunk_id,
            section_label=candidate.section.section_label,
            content=candidate.section.content,
            score=round(candidate.score, 4),
            keyword_score=round(candidate.keyword_score, 4),
            semantic_score=round(candidate.semantic_score, 4),
            metadata_score=round(candidate.metadata_score, 4),
            reasons=candidate.reasons,
            source_type=candidate.section.source_type,
            source_url=candidate.section.source_url,
            topics=candidate.section.topics,
            keywords=candidate.section.keywords,
            technologies=candidate.section.technologies,
        )

    def _citation_history_read(self, citation: CitationHistory) -> CitationRead:
        return CitationRead(
            citation_key=citation.citation_key,
            document_id=citation.document_id,
            document_title=citation.title,
            chunk_id=citation.chunk_id,
            snippet=citation.snippet,
            source_url=citation.source_url,
            section_label=citation.section_label,
            relevance_score=round(citation.relevance_score, 4),
        )

    def _section_id(self, document_id: str, chunk_id: str | None) -> str:
        return f"{document_id}:{chunk_id or 'document'}"
