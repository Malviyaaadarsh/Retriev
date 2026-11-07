"""File-extension based extractor factory."""

from pathlib import Path
from typing import Type

from .base.extractor import BaseExtractor
from .extractors import CSVExtractor, DocxExtractor, MarkdownExtractor, PDFExtractor, TXTExtractor


class UnsupportedFileTypeError(ValueError):
    """Raised when no extractor is registered for a file extension."""


class ExtractorFactory:
    """Resolve a supported extension to an extractor implementation."""

    _extractors: dict[str, Type[BaseExtractor]] = {
        ".pdf": PDFExtractor,
        ".txt": TXTExtractor,
        ".md": MarkdownExtractor,
        ".docx": DocxExtractor,
        ".csv": CSVExtractor,
    }

    @classmethod
    def get(cls, file_path: str | Path) -> BaseExtractor:
        extension = Path(file_path).suffix.lower()
        extractor_type = cls._extractors.get(extension)
        if extractor_type is None:
            raise UnsupportedFileTypeError(f"Unsupported file type: {extension or '<none>'}")
        return extractor_type()
