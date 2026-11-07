"""SQLite persistence for workspaces, chats, and settings."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, delete, select
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import StorageConfig
from ..exceptions import ChatNotFound, DatabaseError, WorkspaceNotFound
from ..models import ChatMessage, ChatSession, ProviderConfiguration, UserPreferences, Workspace
from .models import (
    Base,
    ChatMessageRecord,
    ChatSessionRecord,
    DocumentRecord,
    ProviderConfigurationRecord,
    UserPreferencesRecord,
    WorkspaceRecord,
    utc_now,
)

logger = logging.getLogger(__name__)


class SQLiteService:
    """Persist relational application state in SQLite."""

    def __init__(self, config: StorageConfig) -> None:
        self.config = config
        Path(config.sqlite_db_path).parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(f"sqlite:///{config.sqlite_db_path}")
        Base.metadata.create_all(self._engine)

    def close(self) -> None:
        self._engine.dispose()

    def health_check(self) -> bool:
        with Session(self._engine) as session:
            session.execute(text("SELECT 1"))
        return True

    def create_workspace(self, name: str, path: str, workspace_id: str | None = None) -> Workspace:
        try:
            record = WorkspaceRecord(
                workspace_id=workspace_id or str(uuid4()),
                name=name,
                path=path,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            with Session(self._engine) as session:
                session.add(record)
                session.commit()
                session.refresh(record)
                return self._workspace(record)
        except Exception as error:
            raise DatabaseError("Unable to create workspace") from error

    def rename_workspace(self, workspace_id: str, name: str) -> Workspace:
        with Session(self._engine) as session:
            record = session.get(WorkspaceRecord, workspace_id)
            if record is None:
                raise WorkspaceNotFound(workspace_id)
            record.name = name
            record.updated_at = utc_now()
            session.commit()
            session.refresh(record)
            return self._workspace(record)

    def list_workspaces(self) -> list[Workspace]:
        with Session(self._engine) as session:
            records = session.scalars(
                select(WorkspaceRecord).order_by(WorkspaceRecord.name)
            ).all()
            return [self._workspace(record) for record in records]

    def get_workspace(self, workspace_id: str) -> Workspace:
        with Session(self._engine) as session:
            record = session.get(WorkspaceRecord, workspace_id)
            if record is None:
                raise WorkspaceNotFound(workspace_id)
            return self._workspace(record)

    def delete_workspace(self, workspace_id: str) -> None:
        with Session(self._engine) as session:
            record = session.get(WorkspaceRecord, workspace_id)
            if record is None:
                raise WorkspaceNotFound(workspace_id)
            session.execute(
                delete(ChatMessageRecord).where(
                    ChatMessageRecord.chat_id.in_(
                        select(ChatSessionRecord.chat_id).where(
                            ChatSessionRecord.workspace_id == workspace_id
                        )
                    )
                )
            )
            session.execute(delete(ChatSessionRecord).where(ChatSessionRecord.workspace_id == workspace_id))
            session.delete(record)
            session.commit()

    def create_chat(self, workspace_id: str, title: str = "") -> ChatSession:
        with Session(self._engine) as session:
            if session.get(WorkspaceRecord, workspace_id) is None:
                raise WorkspaceNotFound(workspace_id)
            record = ChatSessionRecord(
                chat_id=str(uuid4()),
                workspace_id=workspace_id,
                title=title,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return self._chat(record)

    def save_message(self, chat_id: str, role: str, content: str) -> ChatMessage:
        with Session(self._engine) as session:
            chat = session.get(ChatSessionRecord, chat_id)
            if chat is None:
                raise ChatNotFound(chat_id)
            record = ChatMessageRecord(
                message_id=str(uuid4()),
                chat_id=chat_id,
                role=role,
                content=content,
                timestamp=utc_now(),
            )
            chat.updated_at = utc_now()
            session.add(record)
            session.commit()
            session.refresh(record)
            return self._message(record)

    def list_chats(self, workspace_id: str) -> list[ChatSession]:
        with Session(self._engine) as session:
            if session.get(WorkspaceRecord, workspace_id) is None:
                raise WorkspaceNotFound(workspace_id)
            records = session.scalars(
                select(ChatSessionRecord)
                .where(ChatSessionRecord.workspace_id == workspace_id)
                .order_by(ChatSessionRecord.updated_at.desc())
            ).all()
            return [self._chat(record) for record in records]

    def get_chat(self, chat_id: str) -> ChatSession:
        with Session(self._engine) as session:
            record = session.get(ChatSessionRecord, chat_id)
            if record is None:
                raise ChatNotFound(chat_id)
            return self._chat(record)

    def delete_chat(self, chat_id: str) -> None:
        with Session(self._engine) as session:
            record = session.get(ChatSessionRecord, chat_id)
            if record is None:
                raise ChatNotFound(chat_id)
            session.execute(delete(ChatMessageRecord).where(ChatMessageRecord.chat_id == chat_id))
            session.delete(record)
            session.commit()

    def mark_document_indexed(self, workspace_id: str, file_name: str) -> None:
        with Session(self._engine) as session:
            record = session.get(
                DocumentRecord,
                {"workspace_id": workspace_id, "file_name": file_name},
            )
            if record is None:
                record = DocumentRecord(
                    workspace_id=workspace_id,
                    file_name=file_name,
                    indexed=True,
                    indexed_at=utc_now(),
                )
                session.add(record)
            else:
                record.indexed = True
                record.indexed_at = utc_now()
            session.commit()

    def list_document_states(self, workspace_id: str) -> dict[str, bool]:
        with Session(self._engine) as session:
            records = session.scalars(
                select(DocumentRecord).where(DocumentRecord.workspace_id == workspace_id)
            ).all()
            return {record.file_name: record.indexed for record in records}

    def remove_document_state(self, workspace_id: str, file_name: str) -> None:
        with Session(self._engine) as session:
            session.execute(
                delete(DocumentRecord).where(
                    DocumentRecord.workspace_id == workspace_id,
                    DocumentRecord.file_name == file_name,
                )
            )
            session.commit()

    def load_chat_history(self, chat_id: str) -> list[ChatMessage]:
        with Session(self._engine) as session:
            if session.get(ChatSessionRecord, chat_id) is None:
                raise ChatNotFound(chat_id)
            records = session.scalars(
                select(ChatMessageRecord)
                .where(ChatMessageRecord.chat_id == chat_id)
                .order_by(ChatMessageRecord.timestamp)
            ).all()
            return [self._message(record) for record in records]

    def save_preferences(self, preferences: UserPreferences) -> None:
        values = {
            "theme": preferences.theme,
            "default_provider": preferences.default_provider,
            "chunk_size": preferences.chunk_size,
            "embedding_model": preferences.embedding_model,
            "workspace_id": preferences.workspace_id,
            "preferences": preferences.preferences,
        }
        with Session(self._engine) as session:
            for key, value in values.items():
                if value is None:
                    continue
                record = session.get(UserPreferencesRecord, key)
                encoded = json.dumps(value) if not isinstance(value, str) else value
                if record is None:
                    session.add(UserPreferencesRecord(key=key, value=encoded))
                else:
                    record.value = encoded
            session.commit()

    def load_preferences(self) -> UserPreferences:
        with Session(self._engine) as session:
            values = {
                record.key: record.value
                for record in session.scalars(select(UserPreferencesRecord)).all()
            }
        return UserPreferences(
            theme=values.get("theme"),
            default_provider=values.get("default_provider"),
            chunk_size=int(values["chunk_size"]) if "chunk_size" in values else None,
            embedding_model=values.get("embedding_model"),
            workspace_id=values.get("workspace_id"),
            preferences=json.loads(values["preferences"]) if "preferences" in values else None,
        )

    @staticmethod
    def _workspace(record: WorkspaceRecord) -> Workspace:
        return Workspace(record.workspace_id, record.name, record.path, record.created_at, record.updated_at)

    @staticmethod
    def _chat(record: ChatSessionRecord) -> ChatSession:
        return ChatSession(record.chat_id, record.workspace_id, record.title, record.created_at, record.updated_at)

    @staticmethod
    def _message(record: ChatMessageRecord) -> ChatMessage:
        return ChatMessage(record.message_id, record.chat_id, record.role, record.content, record.timestamp)
