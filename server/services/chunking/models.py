"""Canonical chunking models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Chunk:
    """A retrieval-ready text chunk and its source metadata."""

    chunk_id: str
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ChunkedDocument:
    """All chunks produced from one cleaned document."""

    file_name: str
    file_type: str
    total_chunks: int
    chunks: list[Chunk]


@dataclass(frozen=True)
class ChunkStatistics:
    """Size statistics for a chunking operation."""

    total_chunks: int
    average_chunk_size: float
    minimum_chunk_size: int
    maximum_chunk_size: int
