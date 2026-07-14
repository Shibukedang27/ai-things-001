from retrieval.citations import CitationGenerator
from retrieval.confidence import ConfidenceCalculator
from retrieval.optimizer import ResponseOptimizer
from retrieval.types import Citation, QueryIntent, QueryProfile, ReasonedAnswer, ReasoningStep, RetrievalCandidate
from retrieval.utils import stable_hash
from retrieval.validation import KnowledgeValidationService


class ReasoningEngine:
    def __init__(
        self,
        validator: KnowledgeValidationService | None = None,
        citation_generator: CitationGenerator | None = None,
        confidence_calculator: ConfidenceCalculator | None = None,
        optimizer: ResponseOptimizer | None = None,
    ) -> None:
        self.validator = validator or KnowledgeValidationService()
        self.citation_generator = citation_generator or CitationGenerator()
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()
        self.optimizer = optimizer or ResponseOptimizer()

    def reason(self, profile: QueryProfile, candidates: list[RetrievalCandidate], *, cache_key: str) -> ReasonedAnswer:
        validation = self.validator.validate(profile, candidates)
        citations = self.citation_generator.generate(candidates)
        evidence = self._supporting_evidence(candidates, citations)
        steps = self._reasoning_steps(profile, candidates, evidence, validation)
        confidence = self.confidence_calculator.calculate(candidates, validation)
        answer = self.optimizer.optimize(
            intent=profile.intent,
            answer=self._draft_answer(profile, candidates, evidence, validation),
            citations=citations,
        )
        return ReasonedAnswer(
            answer=answer,
            confidence_score=confidence,
            citations=citations,
            retrieved_sections=candidates,
            reasoning_path=steps,
            supporting_evidence=evidence,
            validation=validation,
            cache_key=cache_key,
        )

    def _draft_answer(
        self,
        profile: QueryProfile,
        candidates: list[RetrievalCandidate],
        evidence: list[str],
        validation: dict[str, object],
    ) -> str:
        if not candidates:
            return (
                "I could not find enough grounded material in the indexed knowledge base to answer this reliably. "
                "Add or index more source documents, then retry the question."
            )
        source_titles = list(dict.fromkeys(candidate.section.document_title for candidate in candidates[:5]))
        evidence_text = " ".join(evidence[:3])
        if profile.intent == QueryIntent.COMPARISON:
            return (
                f"Across {len(source_titles)} source document(s), the main comparison should focus on purpose, "
                f"implementation complexity, trade-offs, and evidence strength. {evidence_text}"
            )
        if profile.intent == QueryIntent.IMPLEMENTATION_REQUEST:
            return (
                "Start with the concepts that recur in the highest-ranked sections, define the data flow, "
                "then implement the smallest verifiable path before optimization. "
                f"{evidence_text}"
            )
        if profile.intent == QueryIntent.DEFINITION:
            return f"The concept is best understood from the retrieved source context: {evidence_text}"
        if profile.intent == QueryIntent.ROADMAP_REQUEST:
            return (
                "Learn the prerequisite concepts first, then the central mechanisms, then implementation trade-offs. "
                f"Recommended next topics are drawn from {', '.join(source_titles)}. {evidence_text}"
            )
        if profile.intent == QueryIntent.INTERVIEW_QUESTION:
            return (
                "Use a concise definition, mention why it matters, then ground the answer in one concrete "
                "source-backed "
                f"example. {evidence_text}"
            )
        if validation.get("has_contradictions"):
            return (
                "The sources contain contrast signals, so the safest answer is to separate what is directly supported "
                f"from what needs verification. {evidence_text}"
            )
        return f"The indexed sources support this synthesis: {evidence_text}"

    def _supporting_evidence(self, candidates: list[RetrievalCandidate], citations: list[Citation]) -> list[str]:
        evidence: list[str] = []
        for candidate, citation in zip(candidates, citations, strict=False):
            evidence.append(f"[{citation.citation_key}] {candidate.section.document_title}: {citation.snippet}")
        return evidence

    def _reasoning_steps(
        self,
        profile: QueryProfile,
        candidates: list[RetrievalCandidate],
        evidence: list[str],
        validation: dict[str, object],
    ) -> list[ReasoningStep]:
        source_count = len({candidate.section.document_id for candidate in candidates})
        return [
            ReasoningStep(
                step_index=1,
                step_type="intent_detection",
                description=f"Detected query intent as {profile.intent.value}.",
                evidence=[profile.sanitized_query],
                confidence_score=0.9,
            ),
            ReasoningStep(
                step_index=2,
                step_type="retrieval_synthesis",
                description=(
                    "Combined keyword, semantic, and metadata signals across "
                    f"{source_count} source document(s)."
                ),
                evidence=evidence[:3],
                confidence_score=0.86 if candidates else 0.2,
            ),
            ReasoningStep(
                step_index=3,
                step_type="validation",
                description="Checked missing query terms, source coverage, and contradiction signals.",
                evidence=[str(validation)],
                confidence_score=0.82 if validation.get("is_answerable") else 0.45,
            ),
            ReasoningStep(
                step_index=4,
                step_type="generation",
                description="Generated a source-grounded answer with citations and confidence.",
                evidence=[stable_hash(*evidence) if evidence else "no_evidence"],
                confidence_score=0.84 if candidates else 0.25,
            ),
        ]
