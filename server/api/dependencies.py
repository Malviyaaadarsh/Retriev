
"""Shared API dependencies and singleton pipeline construction."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from server.path import APP_PATHS
from server.pipelines.chat import ChatPipeline
from server.pipelines.ingestion import IngestionPipeline
from server.services.embedding.providers.minilm_provider import MiniLMProvider
from server.services.retrieval import RetrievalConfig, RetrievalService
from server.services.storage import StorageService
from server.services.storage.config import StorageConfig

_storage_service: StorageService | None = None
_ingestion_pipeline: IngestionPipeline | None = None
_chat_pipeline: ChatPipeline | None = None
_embedding_provider: MiniLMProvider | None = None


def get_storage_service() -> StorageService:
    global _storage_service

    if _storage_service is None:
        APP_PATHS.ensure_runtime_dirs()

        _storage_service = StorageService(
            StorageConfig(
                vector_db_path=str(APP_PATHS.vector_db),
                sqlite_db_path=str(APP_PATHS.sqlite_db),
            )
        )

    return _storage_service


def get_ingestion_pipeline() -> IngestionPipeline:
    global _ingestion_pipeline

    if _ingestion_pipeline is None:
        _ingestion_pipeline = IngestionPipeline(get_storage_service())

    return _ingestion_pipeline


def get_chat_pipeline() -> ChatPipeline:
    global _chat_pipeline

    if _chat_pipeline is None:
        storage = get_storage_service()
        _chat_pipeline = ChatPipeline(
            RetrievalService(
                get_embedding_provider(),
                storage.vectors,
                RetrievalConfig(top_k=5),
            )
        )

    return _chat_pipeline


def get_embedding_provider() -> MiniLMProvider:
    global _embedding_provider

    if _embedding_provider is None:
        _embedding_provider = MiniLMProvider()
    return _embedding_provider


def check_readiness() -> dict[str, bool | str]:
    """Verify storage and local embedding initialization for desktop startup."""
    storage = get_storage_service()
    checks = storage.health_check()
    try:
        get_embedding_provider().embed("Retriev readiness probe")
        embedding_model = True
        detail = None
    except Exception as error:
        embedding_model = False
        detail = str(error)
    return {
        "sqlite": checks["sqlite"],
        "lancedb": checks["lancedb"],
        "embedding_model": embedding_model,
        "detail": detail,
    }


StorageDependency = Annotated[StorageService, Depends(get_storage_service)]
IngestionDependency = Annotated[IngestionPipeline, Depends(get_ingestion_pipeline)]
ChatDependency = Annotated[ChatPipeline, Depends(get_chat_pipeline)]
