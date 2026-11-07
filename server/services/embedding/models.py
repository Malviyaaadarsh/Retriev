"""Canonical embedding models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EmbeddedChunk:
    chunk_id: str
    content: str
    embedding: list[float]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class EmbeddedDocument:
    file_name: str
    total_chunks: int
    embedded_chunks: list[EmbeddedChunk]


@dataclass(frozen=True)
class EmbeddingStatistics:
    total_chunks: int
    embedding_dimension: int
    total_time: float
    average_time_per_chunk: float
