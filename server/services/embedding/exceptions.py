"""Embedding-specific exceptions."""


class EmbeddingError(RuntimeError):
    """Base error for embedding failures."""


class ModelLoadError(EmbeddingError):
    """Raised when the configured embedding model cannot be loaded."""


class InvalidEmbeddingDimension(EmbeddingError):
    """Raised when vectors do not share one consistent dimension."""
