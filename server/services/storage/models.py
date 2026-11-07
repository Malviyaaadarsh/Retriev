"""Public storage data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Workspace:
    workspace_id: str
    name: str
    path: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ChatSession:
    chat_id: str
    workspace_id: str
    title: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ChatMessage:
    message_id: str
    chat_id: str
    role: str
    content: str
    timestamp: datetime


@dataclass(frozen=True)
class ProviderConfiguration:
    provider_name: str
    model_name: str
    api_key_reference: str | None
    enabled: bool


@dataclass(frozen=True)
class UserPreferences:
    theme: str | None = None
    default_provider: str | None = None
    chunk_size: int | None = None
    embedding_model: str | None = None
    workspace_id: str | None = None
    preferences: dict[str, Any] | None = None
