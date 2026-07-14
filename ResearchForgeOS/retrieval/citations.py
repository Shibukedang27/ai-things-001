from retrieval.types import Citation, RetrievalCandidate
from retrieval.utils import compress_text, tokenize


class CitationGenerator:
    def generate(self, candidates: list[RetrievalCandidate]) -> list[Citation]:
        citations: list[Citation] = []
        for index, candidate in enumerate(candidates, start=1):
            citation_key = f"D{index}"
            snippet = compress_text(
                candidate.section.content,
                tokenize(candidate.section.document_title),
                max_characters=360,
            )
            citations.append(
                Citation(
                    citation_key=citation_key,
                    document_id=candidate.section.document_id,
                    document_title=candidate.section.document_title,
                    snippet=snippet,
                    relevance_score=candidate.score,
                    chunk_id=candidate.section.chunk_id,
                    source_url=candidate.section.source_url,
                    section_label=candidate.section.section_label,
                )
            )
        return citations
