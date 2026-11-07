"""Exceptions raised by the chat pipeline."""


class ChatPipelineError(Exception):
    """Base exception for chat orchestration failures."""


class InvalidQueryError(ChatPipelineError):
    """The request query is missing or contains only whitespace."""


class RetrievalPipelineError(ChatPipelineError):
    """Retrieval failed while handling a chat request."""


class PromptPipelineError(ChatPipelineError):
    """Prompt construction failed while handling a chat request."""


class GenerationPipelineError(ChatPipelineError):
    """Answer generation failed while handling a chat request."""
