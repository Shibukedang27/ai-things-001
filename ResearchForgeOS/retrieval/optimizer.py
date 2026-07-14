from retrieval.types import Citation, QueryIntent


class ResponseOptimizer:
    def optimize(self, *, intent: QueryIntent, answer: str, citations: list[Citation]) -> str:
        citation_keys = " ".join(f"[{citation.citation_key}]" for citation in citations[:4])
        if not citation_keys:
            citation_keys = "[no direct source]"
        prefix = {
            QueryIntent.COMPARISON: "Comparison:",
            QueryIntent.IMPLEMENTATION_REQUEST: "Implementation strategy:",
            QueryIntent.DEFINITION: "Definition:",
            QueryIntent.RESEARCH_REQUEST: "Research synthesis:",
            QueryIntent.CODING_HELP: "Coding guidance:",
            QueryIntent.INTERVIEW_QUESTION: "Interview-ready answer:",
            QueryIntent.SUMMARY_REQUEST: "Summary:",
            QueryIntent.ROADMAP_REQUEST: "Learning roadmap:",
            QueryIntent.QUESTION: "Answer:",
        }[intent]
        return f"{prefix} {answer.strip()} {citation_keys}".strip()
