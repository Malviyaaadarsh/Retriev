"""Canonical generation models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Citation:
    file_name: str
    page: int | None
    chunk_id: str
    excerpt: str = ""


@dataclass(frozen=True)
class GenerationResult:
    answer: str
    citations: list[Citation]
    provider_name: str
    model_name: str
    generation_time_ms: float


@dataclass(frozen=True)
class GenerationStatistics:
    generation_time_ms: float
    provider: str
    model: str
    answer_length: int
    citation_count: int
