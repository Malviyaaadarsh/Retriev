"""Canonical models returned by every document extractor."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DocumentUnit:
    """A retrieval-sized unit of content and its source metadata."""

    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ExtractedDocument:
    """The common extraction result independent of source file format."""

    file_name: str
    file_path: str
    file_type: str
    units: list[DocumentUnit]
