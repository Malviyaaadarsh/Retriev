"""Prompt assembly and source reference creation."""

from typing import Any

from server.services.retrieval.models import RetrievedChunk, RetrievalResult

from .config import PromptBuilderConfig
from .models import PromptContext, SourceReference
from .templates import DEFAULT_SYSTEM_PROMPT, PromptTemplate


class PromptBuilder:
    """Build grounded prompts from ranked retrieval results."""

    def __init__(self, config: PromptBuilderConfig | None = None) -> None:
        self.config = config or PromptBuilderConfig()
        if self.config.max_context_chunks < 0:
            raise ValueError("max_context_chunks cannot be negative")

    def build(self, query: str, retrieval_result: RetrievalResult) -> PromptContext:
        chunks = retrieval_result.chunks[: self.config.max_context_chunks]
        context = self._assemble_context(chunks)
        source_metadata = [
            self._source_metadata(chunk)
            for chunk in chunks
        ] if self.config.include_sources else []
        final_prompt = PromptTemplate.render(DEFAULT_SYSTEM_PROMPT, context, query)
        return PromptContext(
            query=query,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            context=context,
            final_prompt=final_prompt,
            source_metadata=source_metadata,
        )

    def _assemble_context(self, chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant context was found."
        return "\n\n".join(
            self._format_chunk(index, chunk)
            for index, chunk in enumerate(chunks, start=1)
        )

    def _format_chunk(self, index: int, chunk: RetrievedChunk) -> str:
        metadata = chunk.metadata
        if not self.config.include_metadata:
            return f"[Source {index}]\n\nContent:\n{chunk.content}"
        return (
            f"[Source {index}]\n\n"
            f"File:\n{metadata.get('file_name', metadata.get('source_file', 'Unknown'))}\n\n"
            f"Page:\n{metadata.get('page', 'Unknown')}\n\n"
            f"Score:\n{chunk.score}\n\n"
            f"Chunk ID:\n{chunk.chunk_id}\n\n"
            f"Content:\n{chunk.content}\n\n"
            "----------------------------------"
        )

    @staticmethod
    def _source_metadata(chunk: RetrievedChunk) -> dict[str, Any]:
        metadata = dict(chunk.metadata)
        metadata.update(
            {
                "chunk_id": chunk.chunk_id,
                "file_name": metadata.get(
                    "file_name",
                    metadata.get("source_file", "Unknown"),
                ),
                "page": metadata.get("page"),
                "score": chunk.score,
                "excerpt": chunk.content,
            }
        )
        return metadata
