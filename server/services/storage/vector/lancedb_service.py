"""Workspace-isolated LanceDB persistence."""

import hashlib
import json
import logging
import re
from typing import Any

import lancedb

from server.services.embedding.models import EmbeddedDocument

from ..config import StorageConfig
from ..exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class LanceDBService:
    """Store and search vectors in one isolated LanceDB table per workspace."""

    def __init__(self, config: StorageConfig) -> None:
        self.config = config
        self._database = lancedb.connect(config.vector_db_path)

    def _table_name(self, workspace_id: str) -> str:
        safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", workspace_id).strip("_")[:40]
        digest = hashlib.sha256(workspace_id.encode("utf-8")).hexdigest()[:12]
        return f"workspace_{safe_id or 'default'}_{digest}"

    def _table_exists(self, name: str) -> bool:
        return name in self._database.list_tables().tables

    def workspace_exists(self, workspace_id: str) -> bool:
        return self._table_exists(self._table_name(workspace_id))

    def health_check(self) -> bool:
        self._database.list_tables()
        return True

    def create_workspace_table(self, workspace_id: str) -> Any:
        try:
            name = self._table_name(workspace_id)
            if self._table_exists(name):
                return self._database.open_table(name)
            return None
        except Exception as error:
            raise VectorStoreError(f"Unable to create table for workspace '{workspace_id}'") from error

    def insert_chunks(self, workspace_id: str, document: EmbeddedDocument) -> int:
        try:
            rows = [
                {
                    "chunk_id": chunk.chunk_id,
                    "workspace_id": workspace_id,
                    "file_name": document.file_name,
                    "file_type": chunk.metadata.get("file_type", ""),
                    "content": chunk.content,
                    "embedding": chunk.embedding,
                    "metadata": json.dumps(
                        {**chunk.metadata, "workspace_id": workspace_id},
                        ensure_ascii=False,
                    ),
                }
                for chunk in document.embedded_chunks
            ]
            name = self._table_name(workspace_id)
            if not rows:
                return 0
            if self._table_exists(name):
                table = self._database.open_table(name)
                escaped_file_name = document.file_name.replace("'", "''")
                table.delete(f"file_name = '{escaped_file_name}'")
                table.add(rows)
            else:
                self._database.create_table(name, data=rows)
            logger.info(
                "Workspace vectors inserted | Workspace: %s | Vector Records: %d",
                workspace_id,
                len(rows),
            )
            return len(rows)
        except VectorStoreError:
            raise
        except Exception as error:
            raise VectorStoreError(f"Unable to insert vectors for '{workspace_id}'") from error

    def delete_workspace(self, workspace_id: str) -> None:
        try:
            name = self._table_name(workspace_id)
            if self._table_exists(name):
                self._database.drop_table(name)
        except Exception as error:
            raise VectorStoreError(f"Unable to delete vectors for '{workspace_id}'") from error

    def update_metadata(self, workspace_id: str, chunk_id: str, metadata: dict[str, Any]) -> None:
        try:
            table = self.create_workspace_table(workspace_id)
            table.update(
                where=f"chunk_id = '{chunk_id.replace(chr(39), chr(39) * 2)}'",
                values={"metadata": json.dumps({**metadata, "workspace_id": workspace_id})},
            )
        except Exception as error:
            raise VectorStoreError(f"Unable to update metadata for '{chunk_id}'") from error

    def search(
        self,
        workspace_id: str,
        query_vector: list[float],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        try:
            name = self._table_name(workspace_id)
            if not self._table_exists(name):
                return []
            return (
                self._database.open_table(name)
                .search(query_vector, vector_column_name="embedding")
                .limit(limit)
                .to_list()
            )
        except Exception as error:
            raise VectorStoreError(f"Unable to search workspace '{workspace_id}'") from error

    def get_document_chunks(self, workspace_id: str, file_name: str) -> list[dict[str, Any]]:
        try:
            name = self._table_name(workspace_id)
            if not self._table_exists(name):
                return []
            escaped = file_name.replace("'", "''")
            rows = self._database.open_table(name).to_arrow().to_pylist()
            return [row for row in rows if row["file_name"] == file_name]
        except Exception as error:
            raise VectorStoreError(f"Unable to load document '{file_name}'") from error
