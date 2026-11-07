"""Input, output, and statistics models for chat orchestration."""

from dataclasses import dataclass, field

from server.services.generation.models import Citation

from .progress import ChatProgress


@dataclass(frozen=True)
class ChatRequest:
    query: str
    workspace_id: str
    provider_name: str
    model_name: str
    api_key: str | None = None


@dataclass(frozen=True)
class ChatStatistics:
    retrieved_chunks: int
    prompt_length: int
    generation_time_ms: float
    total_time_ms: float
    citation_count: int


@dataclass(frozen=True)
class ChatResult:
    query: str
    answer: str
    citations: list[Citation]
    retrieved_chunks: int
    provider_name: str
    model_name: str
    execution_time_ms: float
    statistics: ChatStatistics | None = None
    progress: ChatProgress | None = field(default=None, compare=False)
