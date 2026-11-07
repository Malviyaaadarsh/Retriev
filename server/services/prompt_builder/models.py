"""Canonical prompt builder models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PromptContext:
    query: str
    system_prompt: str
    context: str
    final_prompt: str
    source_metadata: list[dict[str, Any]]


@dataclass(frozen=True)
class SourceReference:
    chunk_id: str
    file_name: str
    page: int | None
    score: float


@dataclass(frozen=True)
class PromptStatistics:
    chunks_used: int
    source_count: int
    prompt_length: int
    context_length: int
