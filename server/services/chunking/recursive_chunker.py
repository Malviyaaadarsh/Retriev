"""Recursive character chunking implementation."""

from collections.abc import Sequence

from .config import ChunkingConfig
from .exceptions import ChunkingError


class RecursiveChunker:
    """Split text using paragraph, line, sentence, space, then character boundaries."""

    def __init__(self, config: ChunkingConfig | None = None) -> None:
        self.config = config or ChunkingConfig()
        self.separators: Sequence[str] = self.config.separators

    def split_text(
        self,
        text: str | None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> list[str]:
        """Return chunks no larger than ``chunk_size`` with contextual overlap."""
        chunk_size = self.config.chunk_size if chunk_size is None else chunk_size
        chunk_overlap = self.config.chunk_overlap if chunk_overlap is None else chunk_overlap
        self._validate_configuration(chunk_size, chunk_overlap)
        if not isinstance(text, str) or not text.strip():
            return []
        normalized = text.strip()
        if len(normalized) <= chunk_size:
            return [normalized]

        content_size = chunk_size - chunk_overlap
        base_chunks = self._recursive_split(normalized, content_size, 0)
        chunks: list[str] = []
        for index, base_chunk in enumerate(base_chunks):
            if index == 0:
                chunks.append(base_chunk)
                continue
            overlap = chunks[-1][-chunk_overlap:] if chunk_overlap else ""
            chunks.append(overlap + base_chunk)
        return chunks

    def _recursive_split(self, text: str, limit: int, separator_index: int) -> list[str]:
        if len(text) <= limit:
            return [text]
        if separator_index >= len(self.separators):
            return [text[start : start + limit] for start in range(0, len(text), limit)]

        separator = self.separators[separator_index]
        if separator and separator not in text:
            return self._recursive_split(text, limit, separator_index + 1)

        parts = list(text) if separator == "" else text.split(separator)
        if len(parts) == 1:
            return self._recursive_split(text, limit, separator_index + 1)

        chunks: list[str] = []
        current = ""
        for part in parts:
            candidate = part if not current else current + separator + part
            if current and len(candidate) > limit:
                chunks.extend(self._recursive_split(current, limit, separator_index + 1))
                current = part
            else:
                current = candidate
        if current:
            chunks.extend(self._recursive_split(current, limit, separator_index + 1))
        return chunks

    @staticmethod
    def _validate_configuration(chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0:
            raise ChunkingError("chunk_size must be greater than zero")
        if chunk_overlap < 0:
            raise ChunkingError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ChunkingError("chunk_overlap must be smaller than chunk_size")
