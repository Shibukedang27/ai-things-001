class KnowledgeEngineError(Exception):
    """Base exception for knowledge engine failures."""


class DocumentParsingError(KnowledgeEngineError):
    """Raised when an input source cannot be parsed into readable text."""
