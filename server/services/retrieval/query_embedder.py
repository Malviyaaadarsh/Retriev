"""Query embedding using the existing embedding provider abstraction."""

from server.services.embedding.providers.base_provider import EmbeddingProvider

from .exceptions import QueryEmbeddingError


class QueryEmbedder:
    """Generate query vectors with the same provider used for documents."""

    def __init__(self, provider: EmbeddingProvider) -> None:
        self._provider = provider

    def embed(self, query: str) -> list[float]:
        try:
            vector = self._provider.embed(query)
            if not vector:
                raise QueryEmbeddingError("Embedding provider returned an empty vector")
            return vector
        except QueryEmbeddingError:
            raise
        except Exception as error:
            raise QueryEmbeddingError("Unable to embed query") from error
