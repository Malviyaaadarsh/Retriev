"""API request schemas."""

from pydantic import BaseModel, Field


class CreateWorkspaceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ChatRequestSchema(BaseModel):
    query: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    provider_name: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    api_key: str | None = None


class ChatMessageRequest(BaseModel):
    role: str = Field(min_length=1)
    content: str = Field(min_length=1)


class CreateChatRequest(BaseModel):
    title: str = ""
    messages: list[ChatMessageRequest] = []
