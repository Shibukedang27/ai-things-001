from pathlib import Path

from knowledge_engine.types import SourceType

EXTENSION_SOURCE_TYPES: dict[str, SourceType] = {
    ".pdf": SourceType.PDF,
    ".docx": SourceType.DOCX,
    ".txt": SourceType.TXT,
    ".md": SourceType.MARKDOWN,
    ".markdown": SourceType.MARKDOWN,
    ".pptx": SourceType.POWERPOINT,
}

MIME_SOURCE_TYPES: dict[str, SourceType] = {
    "application/pdf": SourceType.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": SourceType.DOCX,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": SourceType.POWERPOINT,
    "text/plain": SourceType.TXT,
    "text/markdown": SourceType.MARKDOWN,
}


class FileTypeDetector:
    def detect(
        self,
        *,
        explicit_source_type: SourceType | None = None,
        filename: str | None = None,
        mime_type: str | None = None,
        source_url: str | None = None,
        content: bytes | str | None = None,
    ) -> SourceType:
        if explicit_source_type is not None:
            return explicit_source_type
        if source_url:
            if "github.com" in source_url.lower():
                return SourceType.GITHUB_REPOSITORY
            return SourceType.WEBSITE
        if mime_type:
            normalized_mime = mime_type.split(";")[0].strip().lower()
            if normalized_mime in MIME_SOURCE_TYPES:
                return MIME_SOURCE_TYPES[normalized_mime]
        if filename:
            suffix = Path(filename).suffix.lower()
            if suffix in EXTENSION_SOURCE_TYPES:
                return EXTENSION_SOURCE_TYPES[suffix]
        if isinstance(content, str):
            return SourceType.PLAIN_NOTES
        return SourceType.TXT
