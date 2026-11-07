"""Ollama generation provider."""

import os
from time import perf_counter

from server.services.prompt_builder.models import PromptContext

from ..config import GenerationConfig
from ..exceptions import GenerationFailed, ModelUnavailable
from ..models import GenerationResult
from ..service_helpers import citations_from_prompt
from .base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    """Generate locally through the Ollama Python client."""

    def generate(self, prompt_context: PromptContext) -> GenerationResult:
        started = perf_counter()
        try:
            from ollama import Client

            host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
            response = Client(host=host).generate(
                model=self.config.model_name,
                prompt=prompt_context.final_prompt,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                },
            )
            answer = response["response"] if isinstance(response, dict) else response.response
        except ModuleNotFoundError as error:
            raise ModelUnavailable("The ollama package is not installed") from error
        except Exception as error:
            raise GenerationFailed("Ollama generation failed") from error
        if not isinstance(answer, str) or not answer.strip():
            raise GenerationFailed("Ollama returned an empty answer")
        return GenerationResult(
            answer=answer.strip(),
            citations=citations_from_prompt(prompt_context),
            provider_name=self.config.provider_name,
            model_name=self.config.model_name,
            generation_time_ms=(perf_counter() - started) * 1000,
        )
