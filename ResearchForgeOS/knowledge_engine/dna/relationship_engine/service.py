from knowledge_engine.dna.types import DNAConceptInput, KnowledgeHierarchyItem
from knowledge_engine.utils import dedupe_preserve_order


class KnowledgeDNARelationshipEngine:
    PARENT_TOPIC_MAP: dict[str, list[str]] = {
        "attention": ["Neural Networks", "Sequence Modeling"],
        "transformer": ["Neural Networks", "Deep Learning"],
        "embedding": ["Representation Learning", "Vector Search"],
        "jwt": ["Authentication", "Security"],
        "database": ["Data Systems", "Persistence"],
        "fastapi": ["Backend Engineering", "API Design"],
        "postgresql": ["Data Systems", "Relational Databases"],
        "knowledge graph": ["Graph Systems", "Knowledge Representation"],
    }
    FUTURE_TOPIC_MAP: dict[str, list[str]] = {
        "attention": ["Transformers", "BERT", "GPT", "Vision Transformer", "Retrieval Augmented Generation"],
        "transformer": ["BERT", "GPT", "Vision Transformer", "Mixture of Experts"],
        "embedding": ["Vector Databases", "Semantic Search", "Retrieval Augmented Generation"],
        "knowledge graph": ["Graph Neural Networks", "Citation Graphs", "Ontology Engineering"],
        "jwt": ["OAuth 2.0", "OpenID Connect", "Zero Trust Architecture"],
        "database": ["Query Optimization", "Distributed Databases", "Vector Indexing"],
        "fastapi": ["Async Python", "API Gateway Design", "Service Observability"],
    }

    def parent_topics(self, concepts: list[DNAConceptInput], fallback_topics: list[str]) -> list[str]:
        parents: list[str] = []
        for concept in concepts:
            parents.extend(self._map_by_name(concept.name, self.PARENT_TOPIC_MAP))
        parents.extend(fallback_topics[:4])
        return dedupe_preserve_order(parents)[:10]

    def child_topics(self, concepts: list[DNAConceptInput]) -> list[str]:
        child_candidates = [concept.name for concept in concepts if concept.concept_type != "core"]
        child_candidates.extend(dependency for concept in concepts for dependency in concept.dependencies)
        return dedupe_preserve_order(child_candidates)[:14]

    def sibling_topics(self, concepts: list[DNAConceptInput], technologies: list[str]) -> list[str]:
        names = [concept.name for concept in concepts]
        siblings: list[str] = []
        if any("attention" in name.lower() for name in names):
            siblings.extend(["Convolution", "Recurrent Neural Networks", "Memory Networks"])
        if any("database" in name.lower() for name in names) or technologies:
            siblings.extend(["Search Indexes", "Caching", "Message Queues"])
        return dedupe_preserve_order(siblings)[:12]

    def future_topics(self, concepts: list[DNAConceptInput]) -> list[str]:
        future: list[str] = []
        for concept in concepts:
            future.extend(self._map_by_name(concept.name, self.FUTURE_TOPIC_MAP))
        if not future and concepts:
            future.extend([f"Advanced {concepts[0].name}", f"{concepts[0].name} in Production"])
        return dedupe_preserve_order(future)[:12]

    def knowledge_chains(
        self,
        *,
        prerequisites: list[str],
        primary_concepts: list[str],
        future_topics: list[str],
    ) -> list[list[str]]:
        chain_seed = [*prerequisites[:3], *primary_concepts[:4], *future_topics[:4]]
        if len(chain_seed) < 2:
            return []
        return [chain_seed[index : index + 4] for index in range(0, max(1, len(chain_seed) - 2), 3)][:5]

    def hierarchy(
        self,
        *,
        parent_topics: list[str],
        primary_concepts: list[str],
        child_topics: list[str],
    ) -> list[KnowledgeHierarchyItem]:
        items: list[KnowledgeHierarchyItem] = []
        for parent in parent_topics[:6]:
            for concept in primary_concepts[:4]:
                items.append(
                    KnowledgeHierarchyItem(
                        parent_topic=parent,
                        child_topic=concept,
                        hierarchy_type="parent_child",
                        confidence_score=0.72,
                        evidence=f"{concept} belongs under the broader area {parent}.",
                    )
                )
        for concept in primary_concepts[:4]:
            for child in child_topics[:3]:
                if child != concept:
                    items.append(
                        KnowledgeHierarchyItem(
                            parent_topic=concept,
                            child_topic=child,
                            hierarchy_type="concept_detail",
                            confidence_score=0.66,
                            evidence=f"{child} is a supporting or more specific topic for {concept}.",
                        )
                    )
        return items[:40]

    def research_evolution(
        self,
        parent_topics: list[str],
        primary_concepts: list[str],
        future_topics: list[str],
    ) -> list[str]:
        return dedupe_preserve_order([*parent_topics[:3], *primary_concepts[:4], *future_topics[:5]])[:12]

    def _map_by_name(self, name: str, mapping: dict[str, list[str]]) -> list[str]:
        lower_name = name.lower()
        results: list[str] = []
        for marker, mapped_values in mapping.items():
            if marker in lower_name:
                results.extend(mapped_values)
        return results
