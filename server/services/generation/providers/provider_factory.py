"""Generation provider factory."""

from ..config import GenerationConfig
from ..exceptions import ProviderNotFound
from .base_provider import BaseProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider


class ProviderFactory:
    """Create a configured provider by name."""

    _providers = {
        "ollama": OllamaProvider,
        "gemini": GeminiProvider,
    }

    @classmethod
    def get_provider(
        cls,
        provider_name: str,
        config: GenerationConfig,
        **provider_options: str,
    ) -> BaseProvider:
        provider_type = cls._providers.get(provider_name.lower())
        if provider_type is None:
            raise ProviderNotFound(f"Unsupported generation provider: {provider_name}")
        return provider_type(config, **provider_options)
