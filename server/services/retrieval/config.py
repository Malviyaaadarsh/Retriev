"""Retrieval configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalConfig:
    top_k: int = 5
    similarity_metric: str = "cosine"
    score_threshold: float = 0.0
