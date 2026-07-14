from knowledge_engine.dna.types import DNADocumentInput


class ResearchDomainClassifier:
    DOMAINS: dict[str, tuple[str, ...]] = {
        "Artificial Intelligence": (
            "attention",
            "transformer",
            "neural",
            "embedding",
            "model",
            "training",
            "inference",
            "machine learning",
            "deep learning",
        ),
        "Software Engineering": (
            "api",
            "architecture",
            "database",
            "service",
            "repository",
            "deployment",
            "framework",
        ),
        "Data Systems": (
            "query",
            "index",
            "transaction",
            "postgresql",
            "database",
            "vector",
            "graph",
            "storage",
        ),
        "Security": (
            "jwt",
            "oauth",
            "permission",
            "authentication",
            "authorization",
            "encryption",
        ),
        "Mathematics": (
            "equation",
            "theorem",
            "proof",
            "matrix",
            "gradient",
            "probability",
            "optimization",
        ),
    }

    def classify(self, document: DNADocumentInput) -> str:
        haystack = " ".join(
            [
                document.category,
                document.title,
                " ".join(document.topics),
                " ".join(document.keywords),
                " ".join(concept.name for concept in document.concepts),
                " ".join(technology.name for technology in document.technologies),
                document.cleaned_text[:5000],
            ]
        ).lower()
        scores = {
            domain: sum(1 for marker in markers if marker in haystack)
            for domain, markers in self.DOMAINS.items()
        }
        best_domain, best_score = max(scores.items(), key=lambda item: item[1])
        if best_score == 0:
            return document.category or "General Knowledge"
        return best_domain
