"""Run the complete Retriev service workflow without FastAPI or Ollama."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, TypeVar

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server.services.chunking import ChunkingService
from server.services.cleaning import CleaningService
from server.services.embedding import EmbeddingService
from server.services.embedding.providers.minilm_provider import MiniLMProvider
from server.services.generation import GenerationService
from server.services.ingestion import ExtractionService
from server.services.prompt_builder import PromptBuilderService
from server.services.retrieval import RetrievalConfig, RetrievalService
from server.services.storage import StorageService
from server.services.storage.config import StorageConfig

T = TypeVar("T")


def load_gemini_key() -> str | None:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    env_file = ROOT / "server" / ".env"
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition("=")
        if separator and name.strip() == "GEMINI_API_KEY":
            return value.strip().strip('"').strip("'") or None
    return None


def run_stage(name: str, action: Callable[[], T]) -> T:
    print(f"\n{name}:\nSTART")
    started = time.perf_counter()
    try:
        result = action()
    except Exception as error:
        print(f"FAILED ({time.perf_counter() - started:.2f}s)\nReason: {error}")
        raise
    print(f"SUCCESS ({time.perf_counter() - started:.2f}s)")
    return result


def main() -> int:
    print("=" * 37)
    print("FULL RAG TEST")
    print("=" * 37)

    sample_pdf = ROOT / "tests" / "sample_docs" / "sample.pdf"
    if not sample_pdf.exists():
        print(f"FAILED\nReason: sample PDF not found at {sample_pdf}")
        return 1

    query = "What are the main topics discussed in this document?"
    workspace_id = "integration_test_workspace"
    with TemporaryDirectory(prefix="retriev_integration_") as temporary_directory:
        data_root = Path(temporary_directory)
        extracted = run_stage(
            "Extraction",
            lambda: ExtractionService.extract(sample_pdf),
        )
        if not extracted.units or not any(unit.content.strip() for unit in extracted.units):
            raise RuntimeError("Extraction produced no text")
        print(f"Document: {extracted.file_name}")
        print(f"Pages found: {len(extracted.units)}")

        cleaned = run_stage(
            "Cleaning",
            lambda: CleaningService().clean_document(extracted),
        )
        if len(cleaned.units) != len(extracted.units):
            raise RuntimeError("Cleaning changed unit count")
        if any(unit.metadata != source.metadata for unit, source in zip(cleaned.units, extracted.units)):
            raise RuntimeError("Cleaning did not preserve metadata")
        print(f"Text units cleaned: {len(cleaned.units)}")

        chunked = run_stage(
            "Chunking",
            lambda: ChunkingService().chunk_document(cleaned),
        )
        if not chunked.chunks or len({chunk.chunk_id for chunk in chunked.chunks}) != chunked.total_chunks:
            raise RuntimeError("Chunking produced invalid or duplicate chunk IDs")
        if not all(chunk.metadata for chunk in chunked.chunks):
            raise RuntimeError("Chunk metadata was lost")
        print(f"Chunks generated: {chunked.total_chunks}")

        embedded = run_stage(
            "Embedding",
            lambda: EmbeddingService().embed_document(chunked),
        )
        dimensions = {len(chunk.embedding) for chunk in embedded.embedded_chunks}
        if not embedded.embedded_chunks or len(dimensions) != 1:
            raise RuntimeError("Embeddings are missing or have inconsistent dimensions")
        print(f"Embeddings generated: {embedded.total_chunks}")
        print(f"Embedding dimension: {next(iter(dimensions))}")

        storage = StorageService(
            StorageConfig(
                vector_db_path=str(data_root / "vectors"),
                sqlite_db_path=str(data_root / "metadata.sqlite"),
            )
        )
        workspace = run_stage(
            "Storage",
            lambda: storage.create_workspace(
                "integration_test_workspace",
                str(data_root),
                workspace_id,
            ),
        )
        inserted = storage.store_embedded_document(workspace.workspace_id, embedded)
        if inserted != embedded.total_chunks:
            raise RuntimeError(f"Expected {embedded.total_chunks} stored chunks, got {inserted}")
        print(f"Chunks inserted: {inserted}")

        query_provider = MiniLMProvider()
        retrieval = run_stage(
            "Retrieval",
            lambda: RetrievalService(
                query_provider,
                storage.vectors,
                RetrievalConfig(top_k=5),
            ).retrieve(query, workspace_id),
        )
        if retrieval.total_results == 0:
            raise RuntimeError("Retrieval returned no results")
        print(f"Top K chunks found: {retrieval.total_results}")

        prompt = run_stage(
            "Prompt Building",
            lambda: PromptBuilderService().build_prompt(query, retrieval),
        )
        if not prompt.final_prompt or not prompt.source_metadata:
            raise RuntimeError("Prompt or source metadata is missing")
        print(f"Prompt length: {len(prompt.final_prompt)} characters")
        print(f"Sources attached: {len(prompt.source_metadata)}")

        api_key = load_gemini_key()
        if not api_key:
            print("\nGeneration:\nSKIPPED\nReason: GEMINI_API_KEY is not set")
            answer = None
        else:
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
            try:
                generated = run_stage(
                    "Generation",
                    lambda: GenerationService().generate(
                        prompt,
                        provider_name="gemini",
                        model_name=model_name,
                        api_key=api_key,
                    ),
                )
            except Exception as error:
                storage.close()
                print(f"\nGeneration could not complete with model '{model_name}'.")
                print(f"Reason: {error}")
                print("Set GEMINI_MODEL to an available Gemini model and rerun.")
                return 1
            answer = generated.answer
            citations = generated.citations
            print(f"Generated answer length: {len(answer)} characters")
            print(f"Citations: {len(citations)}")

        print("\n" + "-" * 37)
        print("ANSWER")
        print(answer or "Generation skipped; set GEMINI_API_KEY to run this stage.")
        print("-" * 37)
        print("CITATIONS")
        for source in prompt.source_metadata:
            page = source.get("page", "unknown")
            print(f"{source.get('file_name', 'unknown')} page {page}")
        print("=" * 37)
        storage.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
