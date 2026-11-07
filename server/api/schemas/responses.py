"""API response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    sqlite: bool
    lancedb: bool
    version: str


class ReadinessResponse(BaseModel):
    status: str
    sqlite: bool
    lancedb: bool
    embedding_model: bool
    detail: str | None = None
    version: str


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workspace_id: str
    name: str
    path: str
    created_at: datetime
    updated_at: datetime


class DeleteResponse(BaseModel):
    success: bool


class DocumentResponse(BaseModel):
    file_name: str
    file_type: str
    size_bytes: int
    status: str = "uploaded"
    indexed_at: datetime | None = None


class DocumentDeleteResponse(BaseModel):
    success: bool
    file_name: str


class DocumentPreviewResponse(BaseModel):
    file_name: str
    preview: str
    file_type: str


class NativeImportRequest(BaseModel):
    paths: list[str]


class NativeImportFileResult(BaseModel):
    source_path: str
    file_name: str | None = None
    status: str
    detail: str | None = None


class NativeImportResponse(BaseModel):
    workspace_id: str
    imported: int
    skipped: int
    failed: int
    files: list[NativeImportFileResult]


class IngestionResponse(BaseModel):
    workspace_id: str
    success: bool
    files_processed: int
    files_failed: int
    chunks_generated: int
    embeddings_generated: int
    vectors_stored: int
    total_time_seconds: float
    documents_indexed: int = 0


class CitationResponse(BaseModel):
    file_name: str
    page: int | None
    chunk_id: str
    excerpt: str = ""


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    provider_name: str
    model_name: str
    retrieved_chunks: int
    execution_time_ms: float


class ChatMessageResponse(BaseModel):
    message_id: str
    chat_id: str
    role: str
    content: str
    timestamp: datetime


class ChatSessionResponse(BaseModel):
    chat_id: str
    workspace_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse] = []
