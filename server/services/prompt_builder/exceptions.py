"""Prompt construction exceptions."""


class PromptBuilderError(RuntimeError):
    """Base prompt builder error."""


class EmptyQueryError(PromptBuilderError):
    """Raised when a prompt is requested without a query."""


class PromptConstructionError(PromptBuilderError):
    """Raised when prompt construction fails."""
