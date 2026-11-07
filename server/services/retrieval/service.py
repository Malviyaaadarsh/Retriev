"""Public retrieval service."""

import logging
from time import perf_counter

from server.services.embedding.providers.base_provider import EmbeddingProvider
from server.services.storage.vector.lancedb_service import LanceDBService

from .config import RetrievalConfig
from .exceptions import EmptyQueryError
from .models import RetrievalResult, RetrievalStatistics
from .query_embedder import QueryEmbedder
from .retriever import Retriever

logger = logging.getLogger(__name__)


class RetrievalService:
    """Embed a query and retrieve ranked chunks from one workspace."""

    def __init__(
        self,
        provider: EmbeddingProvider,
        vector_store: LanceDBService,
        config: RetrievalConfig | None = None,
    ) -> None:
        self.config = config or RetrievalConfig()
        self._query_embedder = QueryEmbedder(provider)
        self._retriever = Retriever(vector_store, self.config)
        self.last_statistics = RetrievalStatistics(0.0, 0, 0.0, 0.0)

    def retrieve(self, query: str, workspace_id: str) -> RetrievalResult:
        if not isinstance(query, str) or not query.strip():
            raise EmptyQueryError("Query must not be empty")
        started = perf_counter()
        query_vector = self._query_embedder.embed(query)
        chunks = self._retriever.retrieve(workspace_id, query_vector)
        elapsed = perf_counter() - started
        scores = [chunk.score for chunk in chunks]
        self.last_statistics = RetrievalStatistics(
            query_time=elapsed,
            results_returned=len(chunks),
            average_score=sum(scores) / len(scores) if scores else 0.0,
            top_score=max(scores) if scores else 0.0,
        )
        logger.info(
            "Query: %s | Workspace: %s | Results: %d | Top Score: %.4f | Search Time: %.4fs",
            query,
            workspace_id,
            len(chunks),
            self.last_statistics.top_score,
            elapsed,
        )
        return RetrievalResult(query, len(chunks), chunks)
