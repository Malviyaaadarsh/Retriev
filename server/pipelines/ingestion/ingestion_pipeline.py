"""Orchestration for indexing every supported document in a workspace."""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter

from server.services.chunking import ChunkingService
from server.services.cleaning import CleaningService
from server.services.embedding import EmbeddingService
from server.services.ingestion import ExtractionService
from server.services.storage import StorageService

from .config import IngestionPipelineConfig
from .models import IngestionReport, IngestionResult, IngestionStatistics
from .progress import PipelineProgress

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Coordinate extraction, cleaning, chunking, embedding, and storage."""

    def __init__(
        self,
        storage_service: StorageService,
        config: IngestionPipelineConfig | None = None,
        extraction_service: ExtractionService | None = None,
        cleaning_service: CleaningService | None = None,
        chunking_service: ChunkingService | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.config = config or IngestionPipelineConfig()
        self.storage_service = storage_service
        self.extraction_service = extraction_service or ExtractionService()
        self.cleaning_service = cleaning_service or CleaningService()
        self.chunking_service = chunking_service or ChunkingService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.progress = PipelineProgress()

    def run(self, workspace_id: str, workspace_path: str | Path) -> IngestionResult:
        """Ingest supported files below ``workspace_path/docs``."""
        started = perf_counter()
        self.progress = PipelineProgress()
        statistics = IngestionStatistics()
        reports: list[IngestionReport] = []
        docs_path = Path(workspace_path) / "docs"

        if not docs_path.exists() or not docs_path.is_dir():
            self.progress.warnings.append(f"Documents directory not found: {docs_path}")
            return self._result(workspace_id, statistics, reports, started, success=False)

        files = sorted(path for path in docs_path.rglob("*") if path.is_file())
        self.progress.total_files = len(files)
        self._log("INGESTION STARTED\nWorkspace: %s\nFiles Found: %d", workspace_id, len(files))

        if not files:
            self.progress.warnings.append("Documents directory is empty")
            return self._result(workspace_id, statistics, reports, started, success=False)

        for index, file_path in enumerate(files, start=1):
            self.progress.update(
                current_file=file_path.name,
                current_stage="Discovery",
                file_index=index - 1,
            )
            extension = file_path.suffix.lower().lstrip(".")
            if extension not in self.config.supported_extensions:
                warning = f"Unsupported file skipped: {file_path.name}"
                self.progress.warnings.append(warning)
                reports.append(IngestionReport(file_path.name, "skipped"))
                self._log("%s", warning)
                self.progress.update(file_index=index)
                continue

            try:
                report = self._process_file(workspace_id, file_path, statistics)
                reports.append(report)
                statistics.files_processed += 1
                if report.status == "success":
                    statistics.documents_indexed += 1
            except Exception as error:
                statistics.files_failed += 1
                message = f"{file_path.name}: {error}"
                self.progress.errors.append(message)
                reports.append(IngestionReport(file_path.name, "failed", error=str(error)))
                logger.exception("Ingestion failed for %s", file_path)
                if not self.config.continue_on_error:
                    raise
            finally:
                self.progress.update(file_index=index)

        statistics.processing_time_seconds = perf_counter() - started
        success = statistics.files_processed > 0 and statistics.files_failed == 0
        return IngestionResult(
            workspace_id=workspace_id,
            files_processed=statistics.files_processed,
            files_failed=statistics.files_failed,
            chunks_generated=statistics.chunks_generated,
            embeddings_generated=statistics.embeddings_generated,
            vectors_stored=statistics.vectors_stored,
            documents_indexed=statistics.documents_indexed,
            total_time_seconds=statistics.processing_time_seconds,
            success=success,
            reports=tuple(reports),
            progress=self.progress,
        )

    def _process_file(
        self,
        workspace_id: str,
        file_path: Path,
        statistics: IngestionStatistics,
    ) -> IngestionReport:
        self._log("----------------------------------\n%s", file_path.name)
        self.progress.update(current_stage="Extraction")
        extracted = self.extraction_service.extract(file_path)
        self.progress.update(current_stage="Cleaning")
        cleaned = self.cleaning_service.clean_document(extracted)
        self.progress.update(current_stage="Chunking")
        chunked = self.chunking_service.chunk_document(cleaned)
        statistics.chunks_generated += chunked.total_chunks
        self.progress.update(current_stage="Embedding")
        embedded = self.embedding_service.embed_document(chunked)
        statistics.embeddings_generated += embedded.total_chunks
        self.progress.update(current_stage="Storage")
        stored = self.storage_service.store_embedded_document(workspace_id, embedded)
        statistics.vectors_stored += stored
        self._log("Extraction OK\nCleaning OK\nChunking OK\nEmbedding OK\nStorage OK")
        return IngestionReport(
            file_name=file_path.name,
            status="success",
            chunks=chunked.total_chunks,
            embeddings=embedded.total_chunks,
            vectors_stored=stored,
        )

    def _result(
        self,
        workspace_id: str,
        statistics: IngestionStatistics,
        reports: list[IngestionReport],
        started: float,
        *,
        success: bool,
    ) -> IngestionResult:
        statistics.processing_time_seconds = perf_counter() - started
        return IngestionResult(
            workspace_id=workspace_id,
            files_processed=statistics.files_processed,
            files_failed=statistics.files_failed,
            chunks_generated=statistics.chunks_generated,
            embeddings_generated=statistics.embeddings_generated,
            vectors_stored=statistics.vectors_stored,
            documents_indexed=statistics.documents_indexed,
            total_time_seconds=statistics.processing_time_seconds,
            success=success,
            reports=tuple(reports),
            progress=self.progress,
        )

    def _log(self, message: str, *args: object) -> None:
        if self.config.verbose_logging:
            logger.info(message, *args)
