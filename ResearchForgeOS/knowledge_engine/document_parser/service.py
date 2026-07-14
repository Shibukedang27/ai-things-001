from pathlib import Path

from knowledge_engine.document_parser.detectors import FileTypeDetector
from knowledge_engine.document_parser.extractors import (
    EXTRACTORS_BY_SOURCE_TYPE,
    GitHubRepositoryExtractor,
    TextExtractor,
    WebsiteExtractor,
)
from knowledge_engine.exceptions import DocumentParsingError
from knowledge_engine.types import ExtractedDocument, KnowledgeSourceRequest, SourceType
from knowledge_engine.utils import normalize_space


class DocumentParser:
    def __init__(self, detector: FileTypeDetector | None = None) -> None:
        self.detector = detector or FileTypeDetector()

    def parse(self, request: KnowledgeSourceRequest) -> ExtractedDocument:
        source_type = self.detector.detect(
            explicit_source_type=request.source_type,
            filename=request.filename,
            mime_type=request.mime_type,
            source_url=request.source_url,
            content=request.content,
        )

        metadata: dict[str, object] = {
            "filename": request.filename,
            "mime_type": request.mime_type,
            "source_url": request.source_url,
        }

        if source_type == SourceType.WEBSITE:
            if not request.source_url:
                raise DocumentParsingError("Website source requires a URL.")
            text, url_metadata = WebsiteExtractor().extract(request.source_url)
            metadata.update(url_metadata)
        elif source_type == SourceType.GITHUB_REPOSITORY:
            if not request.source_url:
                raise DocumentParsingError("GitHub repository source requires a URL.")
            text, url_metadata = GitHubRepositoryExtractor().extract(request.source_url)
            metadata.update(url_metadata)
        else:
            if request.content is None:
                raise DocumentParsingError("Document content is required for this source type.")
            extractor = (
                TextExtractor()
                if source_type == SourceType.RESEARCH_PAPER and isinstance(request.content, str)
                else EXTRACTORS_BY_SOURCE_TYPE[source_type]
            )
            text = extractor.extract(request.content)

        cleaned_text = normalize_space(text)
        if len(cleaned_text) < 10:
            raise DocumentParsingError("Document did not contain enough readable text.")

        title = request.title or self._infer_title(cleaned_text, request.filename, metadata)
        author = request.author or self._infer_author(cleaned_text, metadata)
        return ExtractedDocument(
            text=cleaned_text,
            source_type=source_type,
            title=title,
            author=author,
            metadata=metadata,
        )

    def _infer_title(self, text: str, filename: str | None, metadata: dict[str, object]) -> str:
        metadata_title = metadata.get("title")
        if isinstance(metadata_title, str) and metadata_title.strip():
            return metadata_title.strip()[:180]
        first_line = next((line.strip("# ").strip() for line in text.splitlines() if line.strip()), None)
        if first_line and len(first_line.split()) <= 18:
            return first_line[:180]
        if filename:
            return Path(filename).stem.replace("_", " ").replace("-", " ").title()
        return "Untitled Knowledge Source"

    def _infer_author(self, text: str, metadata: dict[str, object]) -> str | None:
        metadata_author = metadata.get("author")
        if isinstance(metadata_author, str) and metadata_author.strip():
            return metadata_author.strip()[:160]
        for line in text.splitlines()[:20]:
            lower = line.lower().strip()
            if lower.startswith("author:") or lower.startswith("authors:"):
                return line.split(":", 1)[1].strip()[:160]
        return None
