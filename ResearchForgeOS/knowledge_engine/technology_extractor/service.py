import re

from knowledge_engine.types import TechnologyCandidate
from knowledge_engine.utils import clamp_score


class TechnologyExtractor:
    TECHNOLOGIES: dict[str, str] = {
        "Python": "language",
        "JavaScript": "language",
        "TypeScript": "language",
        "SQL": "language",
        "FastAPI": "backend_framework",
        "Django": "backend_framework",
        "Flask": "backend_framework",
        "React": "frontend_framework",
        "Next.js": "frontend_framework",
        "Vue": "frontend_framework",
        "PostgreSQL": "database",
        "MySQL": "database",
        "SQLite": "database",
        "Redis": "cache",
        "Docker": "infrastructure",
        "Kubernetes": "infrastructure",
        "AWS": "cloud",
        "GCP": "cloud",
        "Azure": "cloud",
        "OpenAI": "ai_platform",
        "PyTorch": "ml_framework",
        "TensorFlow": "ml_framework",
        "scikit-learn": "ml_framework",
        "LangChain": "ai_framework",
        "LlamaIndex": "ai_framework",
        "Qdrant": "vector_database",
        "Pinecone": "vector_database",
        "Neo4j": "graph_database",
        "GraphQL": "api",
        "REST": "api",
        "JWT": "security",
        "OAuth": "security",
        "Alembic": "database_tooling",
        "SQLAlchemy": "orm",
    }

    def extract(self, text: str) -> list[TechnologyCandidate]:
        candidates: list[TechnologyCandidate] = []
        for technology, category in self.TECHNOLOGIES.items():
            pattern = re.compile(rf"(?<![A-Za-z0-9_.+-]){re.escape(technology)}(?![A-Za-z0-9_.+-])", re.I)
            matches = list(pattern.finditer(text))
            if not matches:
                continue
            evidence = [self._evidence(text, match.start(), match.end()) for match in matches[:3]]
            candidates.append(
                TechnologyCandidate(
                    name=technology,
                    category=category,
                    confidence_score=clamp_score(0.55 + min(0.4, len(matches) * 0.08)),
                    evidence=evidence,
                )
            )
        return sorted(candidates, key=lambda item: (-item.confidence_score, item.name))

    def _evidence(self, text: str, start: int, end: int) -> str:
        left = max(0, start - 90)
        right = min(len(text), end + 90)
        return text[left:right].replace("\n", " ").strip()
