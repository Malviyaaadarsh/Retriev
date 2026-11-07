"""Embedding provider abstraction."""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Provider interface independent of storage and retrieval."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Embed one text value."""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text values in one provider call."""
