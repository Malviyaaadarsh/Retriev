"""Google Gemini generation provider."""

import os
from time import perf_counter

from server.services.prompt_builder.models import PromptContext

from ..config import GenerationConfig
from ..exceptions import GenerationFailed, InvalidApiKey, ModelUnavailable
from ..models import GenerationResult
from ..service_helpers import citations_from_prompt
from .base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    """Generate through the Google Generative AI client."""

    def __init__(self, config: GenerationConfig, api_key: str | None = None) -> None:
        super().__init__(config)
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    def generate(self, prompt_context: PromptContext) -> GenerationResult:
        if not self.api_key:
            raise InvalidApiKey("GOOGLE_API_KEY or GEMINI_API_KEY is required")
        started = perf_counter()
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.config.model_name)
            response = model.generate_content(
                prompt_context.final_prompt,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": self.config.max_tokens,
                },
            )
            answer = response.text
        except ModuleNotFoundError as error:
            raise ModelUnavailable("The google-generativeai package is not installed") from error
        except Exception as error:
            raise GenerationFailed("Gemini generation failed") from error
        if not isinstance(answer, str) or not answer.strip():
            raise GenerationFailed("Gemini returned an empty answer")
        return GenerationResult(
            answer=answer.strip(),
            citations=citations_from_prompt(prompt_context),
            provider_name=self.config.provider_name,
            model_name=self.config.model_name,
            generation_time_ms=(perf_counter() - started) * 1000,
        )
