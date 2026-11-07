"""Document-level embedding service."""

import logging
from time import perf_counter

from server.services.chunking.models import ChunkedDocument

from .config import EmbeddingConfig
from .exceptions import InvalidEmbeddingDimension
from .models import EmbeddedChunk, EmbeddedDocument, EmbeddingStatistics
from .providers.base_provider import EmbeddingProvider
from .providers.minilm_provider import MiniLMProvider

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Batch-embed chunks while preserving IDs, content, and metadata."""

    def __init__(
        self,
        provider: EmbeddingProvider | None = None,
        config: EmbeddingConfig | None = None,
    ) -> None:
        self.config = config or EmbeddingConfig()
        self._provider = provider or MiniLMProvider(self.config)
        self.last_statistics = EmbeddingStatistics(0, 0, 0.0, 0.0)

    def embed_document(self, chunked_document: ChunkedDocument) -> EmbeddedDocument:
        started = perf_counter()
        non_empty_chunks = [chunk for chunk in chunked_document.chunks if chunk.content]
        texts = [chunk.content for chunk in non_empty_chunks]
        vectors = self._provider.embed_batch(texts)

        if len(vectors) != len(non_empty_chunks):
            raise InvalidEmbeddingDimension("Provider returned an incorrect number of vectors")
        dimension = self._validate_dimensions(vectors)
        embedded_chunks = [
            EmbeddedChunk(
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                embedding=vector,
                metadata=dict(chunk.metadata),
            )
            for chunk, vector in zip(non_empty_chunks, vectors)
        ]
        total_time = perf_counter() - started
        self.last_statistics = EmbeddingStatistics(
            total_chunks=len(embedded_chunks),
            embedding_dimension=dimension,
            total_time=total_time,
            average_time_per_chunk=(
                total_time / len(embedded_chunks) if embedded_chunks else 0.0
            ),
        )
        logger.info(
            "%s | Chunks Embedded: %d | Model: %s | Dimension: %d | Time: %.4fs",
            chunked_document.file_name,
            self.last_statistics.total_chunks,
            self.config.model_name,
            dimension,
            total_time,
        )
        return EmbeddedDocument(
            file_name=chunked_document.file_name,
            total_chunks=len(embedded_chunks),
            embedded_chunks=embedded_chunks,
        )

    @staticmethod
    def _validate_dimensions(vectors: list[list[float]]) -> int:
        dimensions = {len(vector) for vector in vectors}
        if len(dimensions) > 1:
            raise InvalidEmbeddingDimension("All embeddings must have the same dimension")
        return next(iter(dimensions), 0)
