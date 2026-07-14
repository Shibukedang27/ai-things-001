from retrieval.types import QueryIntent, QueryProfile
from retrieval.utils import normalize_text, sanitize_query, tokenize


class QueryUnderstandingService:
    def analyze(self, query: str, *, filters: dict[str, object] | None = None) -> QueryProfile:
        sanitized = sanitize_query(query)
        normalized = normalize_text(sanitized)
        intent = self._detect_intent(normalized)
        keywords = tokenize(normalized)
        expanded_queries = self._expand(normalized, intent, keywords)
        return QueryProfile(
            original_query=query,
            sanitized_query=sanitized,
            normalized_query=normalized,
            intent=intent,
            expanded_queries=expanded_queries,
            keywords=keywords,
            filters=filters or {},
        )

    def _detect_intent(self, normalized_query: str) -> QueryIntent:
        if any(signal in normalized_query for signal in ("compare", "versus", " vs ", "difference", "trade-off")):
            return QueryIntent.COMPARISON
        if any(signal in normalized_query for signal in ("implement", "implementation", "build", "architecture")):
            return QueryIntent.IMPLEMENTATION_REQUEST
        if normalized_query.startswith(("what is", "define ", "explain the term", "meaning of")):
            return QueryIntent.DEFINITION
        if any(signal in normalized_query for signal in ("paper", "research", "evidence", "literature", "citation")):
            return QueryIntent.RESEARCH_REQUEST
        if any(signal in normalized_query for signal in ("code", "debug", "error", "api example", "snippet")):
            return QueryIntent.CODING_HELP
        if "interview" in normalized_query:
            return QueryIntent.INTERVIEW_QUESTION
        if any(signal in normalized_query for signal in ("summarize", "summary", "brief", "overview")):
            return QueryIntent.SUMMARY_REQUEST
        if any(signal in normalized_query for signal in ("roadmap", "learn next", "learning path", "study plan")):
            return QueryIntent.ROADMAP_REQUEST
        return QueryIntent.QUESTION

    def _expand(self, normalized_query: str, intent: QueryIntent, keywords: list[str]) -> list[str]:
        intent_terms = {
            QueryIntent.COMPARISON: ["compare", "tradeoffs", "advantages", "limitations"],
            QueryIntent.IMPLEMENTATION_REQUEST: ["implementation", "architecture", "steps", "strategy"],
            QueryIntent.DEFINITION: ["definition", "meaning", "core concept"],
            QueryIntent.RESEARCH_REQUEST: ["evidence", "paper", "method", "findings"],
            QueryIntent.CODING_HELP: ["code", "example", "api", "algorithm"],
            QueryIntent.INTERVIEW_QUESTION: ["interview", "importance", "answer"],
            QueryIntent.SUMMARY_REQUEST: ["summary", "key points", "overview"],
            QueryIntent.ROADMAP_REQUEST: ["roadmap", "prerequisites", "next topics"],
            QueryIntent.QUESTION: ["explanation", "evidence", "context"],
        }
        expansions = [normalized_query]
        terms = intent_terms[intent]
        if keywords:
            expansions.append(" ".join([*keywords[:8], *terms]))
        expansions.append(" ".join(terms))
        return list(dict.fromkeys(expansion for expansion in expansions if expansion.strip()))
