"""Public answer generation service."""

import logging
from time import perf_counter

from server.services.prompt_builder.models import PromptContext

from .config import GenerationConfig
from .models import GenerationResult, GenerationStatistics
from .providers.base_provider import BaseProvider
from .providers.provider_factory import ProviderFactory
from .validator import GenerationValidator

logger = logging.getLogger(__name__)


class GenerationService:
    """Generate answers from PromptContext without retrieval or prompt construction."""

    def __init__(self, provider: BaseProvider | None = None) -> None:
        self._provider = provider
        self.last_statistics = GenerationStatistics(0.0, "", "", 0, 0)

    def generate(
        self,
        prompt_context: PromptContext,
        provider_name: str | None = None,
        model_name: str | None = None,
        **provider_options: str,
    ) -> GenerationResult:
        config = GenerationConfig(
            provider_name=provider_name or (self._provider.config.provider_name if self._provider else ""),
            model_name=model_name or (self._provider.config.model_name if self._provider else ""),
        )
        GenerationValidator.validate(prompt_context, config.model_name)
        provider = self._provider or ProviderFactory.get_provider(
            config.provider_name,
            config,
            **provider_options,
        )
        started = perf_counter()
        result = provider.generate(prompt_context)
        elapsed = (perf_counter() - started) * 1000
        self.last_statistics = GenerationStatistics(
            generation_time_ms=result.generation_time_ms or elapsed,
            provider=result.provider_name,
            model=result.model_name,
            answer_length=len(result.answer),
            citation_count=len(result.citations),
        )
        logger.info(
            "Generation Completed | Provider: %s | Model: %s | Prompt Length: %d chars | "
            "Generation Time: %.2f ms",
            result.provider_name,
            result.model_name,
            len(prompt_context.final_prompt),
            self.last_statistics.generation_time_ms,
        )
        return result
