from knowledge_engine.chunk_manager import ChunkManager
from knowledge_engine.code_block_extractor import CodeBlockExtractor
from knowledge_engine.concept_extractor import ConceptExtractor
from knowledge_engine.document_parser import DocumentParser
from knowledge_engine.embedding_service import EmbeddingService
from knowledge_engine.extractors import AlgorithmExtractor, DefinitionExtractor, EquationExtractor
from knowledge_engine.keyword_extractor import KeywordExtractor
from knowledge_engine.learning_asset_generator import LearningAssetGenerator
from knowledge_engine.metadata_generator import MetadataGenerator
from knowledge_engine.preprocessing import ContentCleaner
from knowledge_engine.reference_extractor import ReferenceExtractor
from knowledge_engine.relationships import RelationshipExtractor
from knowledge_engine.summary_generator import SummaryGenerator
from knowledge_engine.technology_extractor import TechnologyExtractor
from knowledge_engine.types import KnowledgeEngineResult, KnowledgeSourceRequest


class KnowledgeEnginePipeline:
    def __init__(
        self,
        *,
        parser: DocumentParser | None = None,
        cleaner: ContentCleaner | None = None,
        chunk_manager: ChunkManager | None = None,
        keyword_extractor: KeywordExtractor | None = None,
        technology_extractor: TechnologyExtractor | None = None,
        concept_extractor: ConceptExtractor | None = None,
        summary_generator: SummaryGenerator | None = None,
        reference_extractor: ReferenceExtractor | None = None,
        embedding_service: EmbeddingService | None = None,
        learning_asset_generator: LearningAssetGenerator | None = None,
        relationship_extractor: RelationshipExtractor | None = None,
    ) -> None:
        self.parser = parser or DocumentParser()
        self.cleaner = cleaner or ContentCleaner()
        self.chunk_manager = chunk_manager or ChunkManager()
        self.keyword_extractor = keyword_extractor or KeywordExtractor()
        self.technology_extractor = technology_extractor or TechnologyExtractor()
        self.concept_extractor = concept_extractor or ConceptExtractor()
        self.summary_generator = summary_generator or SummaryGenerator()
        self.reference_extractor = reference_extractor or ReferenceExtractor()
        self.embedding_service = embedding_service or EmbeddingService()
        self.learning_asset_generator = learning_asset_generator or LearningAssetGenerator()
        self.relationship_extractor = relationship_extractor or RelationshipExtractor()
        self.metadata_generator = MetadataGenerator()
        self.definition_extractor = DefinitionExtractor()
        self.algorithm_extractor = AlgorithmExtractor()
        self.equation_extractor = EquationExtractor()
        self.code_block_extractor = CodeBlockExtractor()

    def process(self, request: KnowledgeSourceRequest) -> KnowledgeEngineResult:
        extracted = self.parser.parse(request)
        cleaned_text = self.cleaner.clean(extracted.text)
        keywords = self.keyword_extractor.extract(cleaned_text)
        keyword_values = [keyword.value for keyword in keywords]
        metadata = self.metadata_generator.generate(
            text=cleaned_text,
            source_type=extracted.source_type,
            title=extracted.title or request.title or "Untitled Knowledge Source",
            author=extracted.author or request.author,
            requested_category=request.category,
            keywords=keyword_values,
        )
        chunks = self.chunk_manager.split(cleaned_text)
        summaries = self.summary_generator.generate(cleaned_text, title=metadata.title, keywords=keyword_values)
        technologies = self.technology_extractor.extract(cleaned_text)
        concepts = self.concept_extractor.extract(cleaned_text, keywords)
        references = self.reference_extractor.extract(cleaned_text)
        embeddings = self.embedding_service.embed_chunks(chunks)
        relationships = self.relationship_extractor.extract(concepts=concepts, technologies=technologies)
        learning_assets = self.learning_asset_generator.generate(
            concepts=concepts,
            technologies=technologies,
            summaries=summaries,
        )

        return KnowledgeEngineResult(
            source_type=extracted.source_type,
            cleaned_text=cleaned_text,
            metadata=metadata,
            chunks=chunks,
            summaries=summaries,
            concepts=concepts,
            keywords=keywords,
            technologies=technologies,
            definitions=self.definition_extractor.extract(cleaned_text),
            algorithms=self.algorithm_extractor.extract(cleaned_text),
            equations=self.equation_extractor.extract(cleaned_text),
            code_snippets=self.code_block_extractor.extract(extracted.text),
            references=references,
            embeddings=embeddings,
            relationships=relationships,
            learning_assets=learning_assets,
        )
