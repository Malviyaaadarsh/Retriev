"""Public prompt builder service."""

import logging

from server.services.retrieval.models import RetrievalResult

from .builder import PromptBuilder
from .config import PromptBuilderConfig
from .exceptions import EmptyQueryError, PromptConstructionError
from .models import PromptContext, PromptStatistics

logger = logging.getLogger(__name__)


class PromptBuilderService:
    """Construct prompts without calling retrieval, storage, or an LLM."""

    def __init__(self, config: PromptBuilderConfig | None = None) -> None:
        self._builder = PromptBuilder(config)
        self.last_statistics = PromptStatistics(0, 0, 0, 0)

    def build_prompt(self, query: str, retrieval_result: RetrievalResult) -> PromptContext:
        if not isinstance(query, str) or not query.strip():
            raise EmptyQueryError("Query must not be empty")
        try:
            prompt_context = self._builder.build(query, retrieval_result)
        except PromptConstructionError:
            raise
        except Exception as error:
            raise PromptConstructionError("Unable to construct prompt") from error

        chunks_used = min(
            retrieval_result.total_results,
            self._builder.config.max_context_chunks,
            len(retrieval_result.chunks),
        )
        source_count = len(
            {
                item.get("file_name")
                for item in prompt_context.source_metadata
            }
        )
        self.last_statistics = PromptStatistics(
            chunks_used=chunks_used,
            source_count=source_count,
            prompt_length=len(prompt_context.final_prompt),
            context_length=len(prompt_context.context),
        )
        logger.info(
            "Prompt Generated | Query: %s | Chunks Used: %d | Sources: %d documents | Characters: %d",
            query,
            chunks_used,
            source_count,
            len(prompt_context.final_prompt),
        )
        return prompt_context
