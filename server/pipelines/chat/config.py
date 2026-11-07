"""Configuration for chat orchestration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatPipelineConfig:
    """Runtime options for the version-one chat pipeline."""

    allow_empty_context: bool = True
    enable_statistics: bool = True
    enable_citations: bool = True
