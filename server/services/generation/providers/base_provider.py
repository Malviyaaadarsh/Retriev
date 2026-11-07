"""Generation provider abstraction."""

from abc import ABC, abstractmethod

from server.services.prompt_builder.models import PromptContext

from ..config import GenerationConfig
from ..models import GenerationResult


class BaseProvider(ABC):
    """Interface implemented by each supported generation provider."""

    def __init__(self, config: GenerationConfig) -> None:
        self.config = config

    @abstractmethod
    def generate(self, prompt_context: PromptContext) -> GenerationResult:
        """Generate an answer from an already-built prompt."""
