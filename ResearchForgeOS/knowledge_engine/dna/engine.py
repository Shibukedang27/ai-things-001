from dataclasses import replace

from knowledge_engine.dna.classifiers import KnowledgeSignalDetector, ResearchDomainClassifier, TechnologyTaxonomy
from knowledge_engine.dna.graph import KnowledgeGraphBuilder
from knowledge_engine.dna.learning_path import LearningPathGenerator
from knowledge_engine.dna.relationship_engine import KnowledgeDNARelationshipEngine
from knowledge_engine.dna.scoring import KnowledgeDNAScorer
from knowledge_engine.dna.types import DNADocumentInput, KnowledgeDNAResult, RelatedDocumentCandidate
from knowledge_engine.dna.utils import similarity, top_unique


class KnowledgeDNAEngine:
    def __init__(
        self,
        *,
        domain_classifier: ResearchDomainClassifier | None = None,
        signal_detector: KnowledgeSignalDetector | None = None,
        taxonomy: TechnologyTaxonomy | None = None,
        scorer: KnowledgeDNAScorer | None = None,
        relationship_engine: KnowledgeDNARelationshipEngine | None = None,
        learning_path_generator: LearningPathGenerator | None = None,
        graph_builder: KnowledgeGraphBuilder | None = None,
    ) -> None:
        self.domain_classifier = domain_classifier or ResearchDomainClassifier()
        self.signal_detector = signal_detector or KnowledgeSignalDetector()
        self.taxonomy = taxonomy or TechnologyTaxonomy()
        self.scorer = scorer or KnowledgeDNAScorer()
        self.relationship_engine = relationship_engine or KnowledgeDNARelationshipEngine()
        self.learning_path_generator = learning_path_generator or LearningPathGenerator()
        self.graph_builder = graph_builder or KnowledgeGraphBuilder()

    def generate(self, document: DNADocumentInput) -> KnowledgeDNAResult:
        primary_concepts = [concept.name for concept in document.concepts if concept.concept_type == "core"][:10]
        if not primary_concepts:
            primary_concepts = [concept.name for concept in document.concepts[:8]]
        secondary_concepts = [
            concept.name
            for concept in document.concepts
            if concept.name not in primary_concepts
        ][:18]
        prerequisites = self._prerequisites(document)
        advanced_topics = self._advanced_topics(document)
        future_topics = self.relationship_engine.future_topics(document.concepts)
        programming_languages = self.taxonomy.programming_languages(document.technologies)
        frameworks = self.taxonomy.frameworks(document.technologies)
        libraries = self.taxonomy.libraries(document.technologies)
        technologies_used = [technology.name for technology in document.technologies]
        mathematical_topics = self.signal_detector.mathematical_topics(document)
        datasets = self.signal_detector.datasets(document)
        research_papers = self.signal_detector.research_papers(document)
        research_category = self.domain_classifier.classify(document)
        related_documents = self._related_documents(document)

        knowledge_score = self.scorer.knowledge_score(document, mathematical_topics)
        estimated_mastery_time_hours = self.scorer.mastery_hours(document, knowledge_score)
        parent_topics = self.relationship_engine.parent_topics(document.concepts, document.topics)
        child_topics = self.relationship_engine.child_topics(document.concepts)
        sibling_topics = self.relationship_engine.sibling_topics(document.concepts, technologies_used)
        learning_order = top_unique(
            [*prerequisites, *primary_concepts, *secondary_concepts[:5], *future_topics[:4]],
            24,
        )
        learning_path = self.learning_path_generator.generate(
            concepts=document.concepts,
            prerequisites=prerequisites,
            future_topics=future_topics,
            estimated_mastery_time_hours=estimated_mastery_time_hours,
        )
        hierarchy = self.relationship_engine.hierarchy(
            parent_topics=parent_topics,
            primary_concepts=primary_concepts,
            child_topics=child_topics,
        )
        knowledge_chains = self.relationship_engine.knowledge_chains(
            prerequisites=prerequisites,
            primary_concepts=primary_concepts,
            future_topics=future_topics,
        )
        research_evolution = self.relationship_engine.research_evolution(parent_topics, primary_concepts, future_topics)

        partial = KnowledgeDNAResult(
            document_title=document.title,
            difficulty_level=document.difficulty,
            estimated_reading_time_minutes=document.estimated_reading_time_minutes,
            knowledge_score=knowledge_score,
            interview_importance=self.scorer.interview_importance(document),
            industry_relevance=self.scorer.industry_relevance(document),
            implementation_complexity=self.scorer.implementation_complexity(document),
            research_category=research_category,
            primary_concepts=primary_concepts,
            secondary_concepts=secondary_concepts,
            prerequisites=prerequisites,
            advanced_topics=advanced_topics,
            future_learning_topics=future_topics,
            related_documents=related_documents,
            technologies_used=technologies_used,
            programming_languages=programming_languages,
            frameworks=frameworks,
            libraries=libraries,
            algorithms=document.algorithms,
            datasets=datasets,
            research_papers=research_papers,
            learning_order=learning_order,
            estimated_mastery_time_hours=estimated_mastery_time_hours,
            mathematical_topics=mathematical_topics,
            parent_topics=parent_topics,
            child_topics=child_topics,
            sibling_topics=sibling_topics,
            knowledge_chains=knowledge_chains,
            research_evolution=research_evolution,
            nodes=[],
            edges=[],
            hierarchy=hierarchy,
            learning_path=learning_path,
            metadata={
                "engine": "knowledge_dna_v1",
                "document_id": document.id,
                "signals": {
                    "concept_count": len(document.concepts),
                    "technology_count": len(document.technologies),
                    "algorithm_count": len(document.algorithms),
                    "mathematical_topic_count": len(mathematical_topics),
                    "related_document_count": len(related_documents),
                },
            },
        )
        nodes = self.graph_builder.build_nodes(document, partial)
        edges = self.graph_builder.build_edges(document, partial)
        return replace(partial, nodes=nodes, edges=edges)

    def _prerequisites(self, document: DNADocumentInput) -> list[str]:
        from_concepts = [
            prerequisite
            for concept in document.concepts
            for prerequisite in [*concept.prerequisites, *concept.dependencies]
        ]
        inferred: list[str] = []
        text = document.cleaned_text.lower()
        if "attention" in text or "transformer" in text:
            inferred.extend(["Neural Networks", "Backpropagation", "Sequence Modeling"])
        if "embedding" in text or "vector" in text:
            inferred.extend(["Linear Algebra", "Similarity Search"])
        if "database" in text or "postgresql" in text:
            inferred.extend(["Data Modeling", "SQL Fundamentals"])
        if "jwt" in text or "authentication" in text:
            inferred.extend(["HTTP", "Authentication Basics"])
        return top_unique([*from_concepts, *inferred], 14)

    def _advanced_topics(self, document: DNADocumentInput) -> list[str]:
        advanced = [
            concept.name
            for concept in document.concepts
            if concept.difficulty_level in {"advanced", "expert"}
        ]
        if document.equations:
            advanced.append("Mathematical Derivation")
        if document.code_snippet_count:
            advanced.append("Production Implementation")
        return top_unique(advanced, 12)

    def _related_documents(self, document: DNADocumentInput) -> list[RelatedDocumentCandidate]:
        document_signals = [
            *document.topics,
            *document.keywords,
            *[concept.name for concept in document.concepts],
            *[technology.name for technology in document.technologies],
        ]
        related: list[RelatedDocumentCandidate] = []
        for candidate in document.related_document_candidates:
            candidate_signals = [*candidate.topics, *candidate.concepts, *candidate.technologies]
            score, shared = similarity(document_signals, candidate_signals)
            if score > 0:
                related.append(
                    RelatedDocumentCandidate(
                        id=candidate.id,
                        title=candidate.title,
                        category=candidate.category,
                        topics=candidate.topics,
                        concepts=candidate.concepts,
                        technologies=candidate.technologies,
                        similarity_score=score,
                        shared_signals=shared[:12],
                    )
                )
        return sorted(related, key=lambda item: item.similarity_score, reverse=True)[:10]
