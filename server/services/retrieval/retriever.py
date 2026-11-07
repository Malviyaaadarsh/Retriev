"""Vector search and result transformation."""

import json
from typing import Any

from server.services.storage.vector.lancedb_service import LanceDBService

from .config import RetrievalConfig
from .exceptions import WorkspaceNotFound
from .models import RetrievedChunk


class Retriever:
    """Search a workspace's vector table without changing stored data."""

    def __init__(self, vector_store: LanceDBService, config: RetrievalConfig | None = None) -> None:
        self._vector_store = vector_store
        self.config = config or RetrievalConfig()

    def retrieve(self, workspace_id: str, query_vector: list[float]) -> list[RetrievedChunk]:
        if not workspace_id:
            raise WorkspaceNotFound("workspace_id is required")
        if not self._vector_store.workspace_exists(workspace_id):
            raise WorkspaceNotFound(workspace_id)
        rows = self._vector_store.search(
            workspace_id,
            query_vector,
            limit=self.config.top_k,
        )
        chunks = sorted(
            (self._to_chunk(row, workspace_id) for row in rows),
            key=lambda chunk: chunk.score,
            reverse=True,
        )
        return [
            chunk
            for chunk in chunks
            if chunk.score >= self.config.score_threshold
        ][: self.config.top_k]

    @staticmethod
    def _to_chunk(row: dict[str, Any], workspace_id: str) -> RetrievedChunk:
        distance = float(row.get("_distance", row.get("distance", 0.0)))
        score = 1.0 / (1.0 + max(distance, 0.0))
        metadata = row.get("metadata", {})
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        metadata = dict(metadata)
        metadata.setdefault("workspace_id", row.get("workspace_id") or workspace_id)
        return RetrievedChunk(
            chunk_id=str(row["chunk_id"]),
            content=str(row["content"]),
            score=score,
            metadata=metadata,
        )
