"""Generation input validation."""

from server.services.prompt_builder.models import PromptContext

from .exceptions import ModelUnavailable, PromptMissing


class GenerationValidator:
    """Validate prompt and selected model before provider execution."""

    @staticmethod
    def validate(prompt_context: PromptContext, model_name: str) -> None:
        if not prompt_context.final_prompt.strip():
            raise PromptMissing("PromptContext contains no final prompt")
        if not model_name.strip():
            raise ModelUnavailable("A model name is required")
