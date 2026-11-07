"""Generation configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationConfig:
    provider_name: str
    model_name: str
    temperature: float = 0.2
    max_tokens: int = 1024
