"""Embedding configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    provider_name: str = "sentence-transformers"
    model_name: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
