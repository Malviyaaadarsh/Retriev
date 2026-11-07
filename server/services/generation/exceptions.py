"""Generation-specific exceptions."""


class GenerationError(RuntimeError):
    """Base generation error."""


class ProviderNotFound(GenerationError):
    """Raised when a provider is not registered."""


class InvalidApiKey(GenerationError):
    """Raised when a cloud provider has no usable API key."""


class ModelUnavailable(GenerationError):
    """Raised when the selected model cannot be used."""


class PromptMissing(GenerationError):
    """Raised when the prompt context is empty or invalid."""


class GenerationFailed(GenerationError):
    """Raised when provider generation fails."""
