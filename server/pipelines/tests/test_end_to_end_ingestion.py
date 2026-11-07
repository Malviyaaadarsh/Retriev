import json
from pathlib import Path

from server.services.embedding import EmbeddingService
from server.services.embedding.providers.base_provider import EmbeddingProvider
from server.services.storage import StorageService
from server.services.storage.config import StorageConfig

from ..ingestion import IngestionPipeline


class FixedEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


def test_pipeline_orchestrates_real_document_services(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "notes.txt").write_text(
        "Retriev indexes workspace documents for semantic search.",
        encoding="utf-8",
    )
    storage = StorageService(
        StorageConfig(
            vector_db_path=str(tmp_path / "vectors"),
            sqlite_db_path=str(tmp_path / "metadata.sqlite"),
        )
    )

    try:
        pipeline = IngestionPipeline(
            storage,
            embedding_service=EmbeddingService(provider=FixedEmbeddingProvider()),
        )
        result = pipeline.run("workspace-e2e", tmp_path)

        assert result.success is True
        assert result.files_processed == 1
        assert result.chunks_generated > 0
        assert result.embeddings_generated == result.chunks_generated
        assert result.vectors_stored == result.chunks_generated

        stored = storage.vectors.get_document_chunks("workspace-e2e", "notes.txt")
        assert stored
        metadata = json.loads(stored[0]["metadata"])
        assert metadata["workspace_id"] == "workspace-e2e"
        assert metadata["file_name"] == "notes.txt"
    finally:
        storage.close()
