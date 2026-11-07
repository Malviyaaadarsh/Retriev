"""Retrieval-specific exceptions."""


class RetrievalError(RuntimeError):
    """Base retrieval error."""


class WorkspaceNotFound(RetrievalError):
    """Raised when a workspace is not available for retrieval."""


class QueryEmbeddingError(RetrievalError):
    """Raised when a query cannot be embedded."""


class EmptyQueryError(RetrievalError):
    """Raised when a query is empty."""
