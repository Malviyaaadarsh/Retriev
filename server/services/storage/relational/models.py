"""SQLAlchemy models for application metadata."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class WorkspaceRecord(Base):
    __tablename__ = "workspaces"
    workspace_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ChatSessionRecord(Base):
    __tablename__ = "chat_sessions"
    chat_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.workspace_id"))
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ChatMessageRecord(Base):
    __tablename__ = "chat_messages"
    message_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    chat_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.chat_id"))
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class DocumentRecord(Base):
    __tablename__ = "documents"
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.workspace_id"), primary_key=True
    )
    file_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProviderConfigurationRecord(Base):
    __tablename__ = "provider_configurations"
    provider_name: Mapped[str] = mapped_column(String(128), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(255))
    api_key_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class UserPreferencesRecord(Base):
    __tablename__ = "user_preferences"
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
