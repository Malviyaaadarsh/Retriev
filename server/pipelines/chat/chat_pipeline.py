"""Orchestrate retrieval, prompt construction, and answer generation."""

from __future__ import annotations

import logging
from time import perf_counter

from server.services.generation import GenerationService
from server.services.prompt_builder import PromptBuilderService
from server.services.retrieval import RetrievalService

from .config import ChatPipelineConfig
from .exceptions import (
    GenerationPipelineError,
    InvalidQueryError,
    PromptPipelineError,
    RetrievalPipelineError,
)
from .models import ChatRequest, ChatResult, ChatStatistics
from .progress import ChatProgress

logger = logging.getLogger(__name__)


class ChatPipeline:
    """Coordinate the RAG question-answering services."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        prompt_builder_service: PromptBuilderService | None = None,
        generation_service: GenerationService | None = None,
        config: ChatPipelineConfig | None = None,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.prompt_builder_service = prompt_builder_service or PromptBuilderService()
        self.generation_service = generation_service or GenerationService()
        self.config = config or ChatPipelineConfig()
        self.progress = ChatProgress()

    def run(self, request: ChatRequest) -> ChatResult:
        """Run the complete chat flow for one request."""
        started = perf_counter()
        self.progress = ChatProgress()
        self._log(
            "CHAT PIPELINE\nQuery: %s\nWorkspace: %s",
            request.query,
            request.workspace_id,
        )
        self._validate_request(request)

        self.progress.update("Retrieving Context", 25.0)
        try:
            retrieval_result = self.retrieval_service.retrieve(
                request.query,
                request.workspace_id,
            )
        except Exception as error:
            self.progress.errors.append(str(error))
            raise RetrievalPipelineError("Unable to retrieve context") from error

        if not self.config.allow_empty_context and retrieval_result.total_results == 0:
            error = RetrievalPipelineError("No relevant context was found")
            self.progress.errors.append(str(error))
            raise error

        self.progress.update("Building Prompt", 50.0)
        try:
            prompt_context = self.prompt_builder_service.build_prompt(
                request.query,
                retrieval_result,
            )
        except Exception as error:
            self.progress.errors.append(str(error))
            raise PromptPipelineError("Unable to build prompt") from error

        self.progress.update("Generating Answer", 75.0)
        generation_started = perf_counter()
        try:
            generation_kwargs = {
                "provider_name": request.provider_name,
                "model_name": request.model_name,
            }
            if request.api_key:
                generation_kwargs["api_key"] = request.api_key
            generation_result = self.generation_service.generate(
                prompt_context,
                **generation_kwargs,
            )
        except Exception as error:
            self.progress.errors.append(str(error))
            raise GenerationPipelineError("Unable to generate answer") from error

        citations = generation_result.citations if self.config.enable_citations else []
        total_time_ms = (perf_counter() - started) * 1000
        generation_time_ms = generation_result.generation_time_ms or (
            (perf_counter() - generation_started) * 1000
        )
        statistics = None
        if self.config.enable_statistics:
            statistics = ChatStatistics(
                retrieved_chunks=retrieval_result.total_results,
                prompt_length=len(prompt_context.final_prompt),
                generation_time_ms=generation_time_ms,
                total_time_ms=total_time_ms,
                citation_count=len(citations),
            )

        self.progress.update("Completed", 100.0)
        self._log(
            "Retrieval: %d chunks\nPrompt: Generated\nProvider: %s\nGeneration: Success\nTime: %.2f ms",
            retrieval_result.total_results,
            generation_result.provider_name,
            total_time_ms,
        )
        return ChatResult(
            query=request.query,
            answer=generation_result.answer,
            citations=citations,
            retrieved_chunks=retrieval_result.total_results,
            provider_name=generation_result.provider_name,
            model_name=generation_result.model_name,
            execution_time_ms=total_time_ms,
            statistics=statistics,
            progress=self.progress,
        )

    def _validate_request(self, request: ChatRequest) -> None:
        if not isinstance(request.query, str) or not request.query.strip():
            error = InvalidQueryError("Query must not be empty")
            self.progress.errors.append(str(error))
            raise error

    @staticmethod
    def _log(message: str, *args: object) -> None:
        logger.info(message, *args)
