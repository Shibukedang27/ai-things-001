import re

from knowledge_engine.dna.types import DNADocumentInput
from knowledge_engine.utils import dedupe_preserve_order


class KnowledgeSignalDetector:
    MATH_TOPICS: dict[str, tuple[str, ...]] = {
        "Linear Algebra": ("matrix", "vector", "eigen", "tensor", "dot product"),
        "Probability": ("probability", "bayes", "distribution", "variance", "expectation"),
        "Optimization": ("gradient", "loss", "objective", "descent", "optimization"),
        "Information Theory": ("entropy", "mutual information", "cross entropy", "kl divergence"),
        "Statistics": ("regression", "correlation", "hypothesis", "confidence interval"),
    }
    DATASET_PATTERN = re.compile(r"\b([A-Z][A-Za-z0-9_-]*(?:Net|Set|Bench|Corpus|Dataset|DB|QA))\b")
    PAPER_PATTERN = re.compile(r"\b([A-Z][A-Za-z0-9: -]{4,120})\s+\((19|20)\d{2}\)")
    COMPANY_MARKERS = ("OpenAI", "Google", "Meta", "Microsoft", "Anthropic", "NVIDIA", "Apple", "Amazon")

    def mathematical_topics(self, document: DNADocumentInput) -> list[str]:
        text = document.cleaned_text.lower()
        topics = [
            topic
            for topic, markers in self.MATH_TOPICS.items()
            if any(marker in text for marker in markers)
        ]
        if document.equations and "Optimization" not in topics:
            topics.append("Optimization")
        return topics

    def datasets(self, document: DNADocumentInput) -> list[str]:
        candidates = [match.group(1) for match in self.DATASET_PATTERN.finditer(document.cleaned_text)]
        blocked = {"ResearchForge", "FastAPI", "PostgreSQL"}
        return [candidate for candidate in dedupe_preserve_order(candidates) if candidate not in blocked][:12]

    def research_papers(self, document: DNADocumentInput) -> list[str]:
        reference_titles = [reference for reference in document.references if len(reference.split()) >= 3]
        inline_titles = [match.group(1).strip() for match in self.PAPER_PATTERN.finditer(document.cleaned_text)]
        return dedupe_preserve_order([*reference_titles, *inline_titles])[:12]

    def companies(self, document: DNADocumentInput) -> list[str]:
        text = document.cleaned_text
        return [company for company in self.COMPANY_MARKERS if company in text]
