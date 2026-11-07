"""Structured output models for ingestion."""

from dataclasses import dataclass, field


@dataclass
class IngestionStatistics:
    """Aggregate counters collected during a pipeline run."""

    files_processed: int = 0
    files_failed: int = 0
    chunks_generated: int = 0
    embeddings_generated: int = 0
    vectors_stored: int = 0
    documents_indexed: int = 0
    processing_time_seconds: float = 0.0


@dataclass(frozen=True)
class IngestionReport:
    """Per-file result included in the detailed pipeline report."""

    file_name: str
    status: str
    chunks: int = 0
    embeddings: int = 0
    vectors_stored: int = 0
    error: str | None = None


@dataclass(frozen=True)
class IngestionResult:
    """Summary returned to API and UI callers."""

    workspace_id: str
    files_processed: int
    files_failed: int
    chunks_generated: int
    embeddings_generated: int
    vectors_stored: int
    total_time_seconds: float
    success: bool
    documents_indexed: int = 0
    reports: tuple[IngestionReport, ...] = field(default_factory=tuple)
    progress: PipelineProgress | None = None
