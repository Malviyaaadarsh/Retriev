"""Document-level chunking service."""

import logging
import re
from time import perf_counter

from server.services.cleaning.models import CleanedDocument

from .config import ChunkingConfig
from .models import Chunk, ChunkStatistics, ChunkedDocument
from .recursive_chunker import RecursiveChunker

logger = logging.getLogger(__name__)


class ChunkingService:
    """Convert cleaned document units into metadata-rich recursive chunks."""

    def __init__(
        self,
        chunker: RecursiveChunker | None = None,
        config: ChunkingConfig | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self.config = config or ChunkingConfig()
        if chunk_size is not None:
            self.config.chunk_size = chunk_size
        if chunk_overlap is not None:
            self.config.chunk_overlap = chunk_overlap
        self._chunker = chunker or RecursiveChunker(self.config)

    def chunk_document(self, cleaned_document: CleanedDocument) -> ChunkedDocument:
        started = perf_counter()
        chunks: list[Chunk] = []
        for unit in cleaned_document.units:
            contents = self._chunker.split_text(
                unit.content,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
            )
            for content in contents:
                chunk_index = len(chunks)
                metadata = dict(unit.metadata)
                metadata.update(
                    {
                        "source_file": cleaned_document.file_name,
                        "file_name": cleaned_document.file_name,
                        "file_type": cleaned_document.file_type,
                        "chunk_index": chunk_index,
                        "chars": len(content),
                        "words": len(re.findall(r"\S+", content)),
                    }
                )
                chunks.append(
                    Chunk(
                        chunk_id=self._chunk_id(cleaned_document.file_name, chunk_index),
                        content=content,
                        metadata=metadata,
                    )
                )

        statistics = self.statistics(chunks)
        logger.info(
            "%s | Chunks Generated: %d | Average Size: %.1f chars | "
            "Chunk Size Config: %d | Overlap Config: %d | Time: %.4fs",
            cleaned_document.file_name,
            statistics.total_chunks,
            statistics.average_chunk_size,
            self.config.chunk_size,
            self.config.chunk_overlap,
            perf_counter() - started,
        )
        return ChunkedDocument(
            file_name=cleaned_document.file_name,
            file_type=cleaned_document.file_type,
            total_chunks=len(chunks),
            chunks=chunks,
        )

    @staticmethod
    def statistics(chunks: list[Chunk]) -> ChunkStatistics:
        sizes = [len(chunk.content) for chunk in chunks]
        if not sizes:
            return ChunkStatistics(0, 0.0, 0, 0)
        return ChunkStatistics(
            total_chunks=len(sizes),
            average_chunk_size=sum(sizes) / len(sizes),
            minimum_chunk_size=min(sizes),
            maximum_chunk_size=max(sizes),
        )

    @staticmethod
    def _chunk_id(file_name: str, index: int) -> str:
        stem = re.sub(r"[^a-zA-Z0-9]+", "_", file_name.rsplit(".", 1)[0]).strip("_").lower()
        return f"{stem or 'document'}_chunk_{index:04d}"
