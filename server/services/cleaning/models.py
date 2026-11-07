"""Models for text cleaning results."""

from dataclasses import dataclass

from server.services.ingestion.base.models import DocumentUnit


@dataclass(frozen=True)
class CleaningResult:
    """Summary of one text-cleaning operation."""

    original_length: int
    cleaned_length: int
    characters_removed: int


@dataclass(frozen=True)
class CleanedDocument:
    """Extracted document with normalized unit content."""

    file_name: str
    file_path: str
    file_type: str
    units: list[DocumentUnit]
