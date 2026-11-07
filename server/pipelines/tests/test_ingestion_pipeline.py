from pathlib import Path

from server.services.chunking.models import Chunk, ChunkedDocument
from server.services.cleaning.models import CleanedDocument
from server.services.embedding.models import EmbeddedChunk, EmbeddedDocument
from server.services.ingestion.base.models import DocumentUnit, ExtractedDocument

from ..ingestion import IngestionPipeline, IngestionPipelineConfig


class FakeExtraction:
    def extract(self, path: Path) -> ExtractedDocument:
        if path.name == "broken.pdf":
            raise ValueError("invalid document")
        return ExtractedDocument(
            file_name=path.name,
            file_path=str(path),
            file_type=path.suffix.lstrip("."),
            units=[DocumentUnit("content for testing", {"page": 1})],
        )


class FakeCleaning:
    def clean_document(self, document: ExtractedDocument) -> CleanedDocument:
        return CleanedDocument(
            document.file_name,
            document.file_path,
            document.file_type,
            document.units,
        )


class FakeChunking:
    def chunk_document(self, document: CleanedDocument) -> ChunkedDocument:
        chunk = Chunk(
            chunk_id=f"{document.file_name}-chunk",
            content=document.units[0].content,
            metadata={"file_name": document.file_name, "page": 1},
        )
        return ChunkedDocument(document.file_name, document.file_type, 1, [chunk])


class FakeEmbedding:
    def embed_document(self, document: ChunkedDocument) -> EmbeddedDocument:
        chunk = document.chunks[0]
        embedded = EmbeddedChunk(
            chunk.chunk_id,
            chunk.content,
            [0.1, 0.2],
            chunk.metadata,
        )
        return EmbeddedDocument(document.file_name, 1, [embedded])


class FakeStorage:
    def __init__(self) -> None:
        self.documents: list[tuple[str, EmbeddedDocument]] = []

    def store_embedded_document(self, workspace_id: str, document: EmbeddedDocument) -> int:
        self.documents.append((workspace_id, document))
        return document.total_chunks


def make_pipeline(config: IngestionPipelineConfig | None = None) -> tuple[IngestionPipeline, FakeStorage]:
    storage = FakeStorage()
    pipeline = IngestionPipeline(
        storage,
        config=config,
        extraction_service=FakeExtraction(),
        cleaning_service=FakeCleaning(),
        chunking_service=FakeChunking(),
        embedding_service=FakeEmbedding(),
    )
    return pipeline, storage


def test_processes_supported_files_and_aggregates_statistics(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    for name in ("one.pdf", "two.md", "three.txt"):
        (docs / name).write_text("content", encoding="utf-8")

    pipeline, storage = make_pipeline()
    result = pipeline.run("workspace-1", tmp_path)

    assert result.success is True
    assert result.files_processed == 3
    assert result.files_failed == 0
    assert result.chunks_generated == 3
    assert result.embeddings_generated == 3
    assert result.vectors_stored == 3
    assert len(storage.documents) == 3
    assert result.progress is not None
    assert result.progress.percentage == 100.0


def test_failure_is_recorded_and_pipeline_continues(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "broken.pdf").write_text("invalid", encoding="utf-8")
    (docs / "valid.txt").write_text("valid", encoding="utf-8")

    pipeline, storage = make_pipeline()
    result = pipeline.run("workspace-1", tmp_path)

    assert result.success is False
    assert result.files_processed == 1
    assert result.files_failed == 1
    assert len(storage.documents) == 1
    assert result.progress is not None
    assert result.progress.errors == ["broken.pdf: invalid document"]
    assert [report.status for report in result.reports] == ["failed", "success"]


def test_unsupported_files_are_skipped_with_warning(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "image.png").write_bytes(b"not processed")

    pipeline, _ = make_pipeline()
    result = pipeline.run("workspace-1", tmp_path)

    assert result.success is False
    assert result.files_processed == 0
    assert result.files_failed == 0
    assert result.reports[0].status == "skipped"
    assert "Unsupported file skipped: image.png" in result.progress.warnings


def test_empty_workspace_returns_unsuccessful_result(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()

    pipeline, _ = make_pipeline()
    result = pipeline.run("workspace-1", tmp_path)

    assert result.success is False
    assert result.files_processed == 0
    assert result.files_failed == 0
    assert result.progress is not None
    assert result.progress.warnings == ["Documents directory is empty"]


def test_continue_on_error_can_be_disabled(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "broken.pdf").write_text("invalid", encoding="utf-8")

    pipeline, _ = make_pipeline(IngestionPipelineConfig(continue_on_error=False))

    try:
        pipeline.run("workspace-1", tmp_path)
    except ValueError as error:
        assert str(error) == "invalid document"
    else:
        raise AssertionError("Expected the file error to be re-raised")
