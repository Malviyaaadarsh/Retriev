"""Unified persistence facade."""

import logging

from server.services.embedding.models import EmbeddedDocument

from .config import StorageConfig
from .models import ChatMessage, ChatSession, UserPreferences, Workspace
from .relational.sqlite_service import SQLiteService
from .vector.lancedb_service import LanceDBService

logger = logging.getLogger(__name__)


class StorageService:
    """Coordinate relational metadata and workspace-isolated vectors."""

    def __init__(self, config: StorageConfig) -> None:
        self.config = config
        self.sqlite = SQLiteService(config)
        self.vectors = LanceDBService(config)

    def close(self) -> None:
        self.sqlite.close()

    def health_check(self) -> dict[str, bool]:
        sqlite_healthy = False
        lancedb_healthy = False
        try:
            sqlite_healthy = self.sqlite.health_check()
        except Exception:
            logger.exception("SQLite health check failed")
        try:
            self.vectors.health_check()
            lancedb_healthy = True
        except Exception:
            logger.exception("LanceDB health check failed")
        return {"sqlite": sqlite_healthy, "lancedb": lancedb_healthy}

    def create_workspace(self, name: str, path: str, workspace_id: str | None = None) -> Workspace:
        workspace = self.sqlite.create_workspace(name, path, workspace_id)
        self.vectors.create_workspace_table(workspace.workspace_id)
        logger.info("Workspace Created | Workspace: %s", workspace.name)
        return workspace

    def list_workspaces(self) -> list[Workspace]:
        return self.sqlite.list_workspaces()

    def get_workspace(self, workspace_id: str) -> Workspace:
        return self.sqlite.get_workspace(workspace_id)

    def delete_workspace(self, workspace_id: str) -> None:
        self.sqlite.delete_workspace(workspace_id)
        self.vectors.delete_workspace(workspace_id)

    def store_embedded_document(self, workspace_id: str, document: EmbeddedDocument) -> int:
        return self.vectors.insert_chunks(workspace_id, document)

    def create_chat(self, workspace_id: str, title: str = "") -> ChatSession:
        return self.sqlite.create_chat(workspace_id, title)

    def save_chat_message(self, chat_id: str, role: str, content: str) -> ChatMessage:
        return self.sqlite.save_message(chat_id, role, content)

    def load_chat_history(self, chat_id: str) -> list[ChatMessage]:
        return self.sqlite.load_chat_history(chat_id)

    def list_chats(self, workspace_id: str) -> list[ChatSession]:
        return self.sqlite.list_chats(workspace_id)

    def get_chat(self, chat_id: str) -> ChatSession:
        return self.sqlite.get_chat(chat_id)

    def delete_chat(self, chat_id: str) -> None:
        self.sqlite.delete_chat(chat_id)

    def mark_document_indexed(self, workspace_id: str, file_name: str) -> None:
        self.sqlite.mark_document_indexed(workspace_id, file_name)

    def list_document_states(self, workspace_id: str) -> dict[str, bool]:
        return self.sqlite.list_document_states(workspace_id)

    def remove_document_state(self, workspace_id: str, file_name: str) -> None:
        self.sqlite.remove_document_state(workspace_id, file_name)

    def save_preferences(self, preferences: UserPreferences) -> None:
        self.sqlite.save_preferences(preferences)

    def load_preferences(self) -> UserPreferences:
        return self.sqlite.load_preferences()
