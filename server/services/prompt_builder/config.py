"""Prompt builder configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptBuilderConfig:
    max_context_chunks: int = 5
    include_metadata: bool = True
    include_sources: bool = True
