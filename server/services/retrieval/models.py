"""Canonical retrieval models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    content: str
    score: float
    metadata: dict[str, Any]


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    total_results: int
    chunks: list[RetrievedChunk]


@dataclass(frozen=True)
class RetrievalStatistics:
    query_time: float
    results_returned: int
    average_score: float
    top_score: float
