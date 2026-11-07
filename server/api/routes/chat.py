from fastapi import APIRouter

from server.api.dependencies import ChatDependency, StorageDependency
from server.api.schemas.errors import PipelineFailureError
from server.api.schemas.errors import InvalidRequestError
from server.api.schemas.requests import ChatMessageRequest, ChatRequestSchema, CreateChatRequest
from server.api.schemas.responses import (
    ChatMessageResponse,
    ChatResponse,
    ChatSessionResponse,
    CitationResponse,
    DeleteResponse,
)
from server.services.storage.exceptions import ChatNotFound, WorkspaceNotFound
from server.pipelines.chat import ChatRequest, InvalidQueryError

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def ask_question(
    request: ChatRequestSchema,
    pipeline: ChatDependency,
) -> ChatResponse:
    try:
        result = pipeline.run(
            ChatRequest(
                query=request.query,
                workspace_id=request.workspace_id,
                provider_name=request.provider_name,
                model_name=request.model_name,
                api_key=request.api_key,
            )
        )
        return ChatResponse(
            answer=result.answer,
            citations=[
                CitationResponse(
                    file_name=citation.file_name,
                    page=citation.page,
                    chunk_id=citation.chunk_id,
                    excerpt=citation.excerpt,
                )
                for citation in result.citations
            ],
            provider_name=result.provider_name,
            model_name=result.model_name,
            retrieved_chunks=result.retrieved_chunks,
            execution_time_ms=result.execution_time_ms,
        )
    except InvalidQueryError as error:
        raise InvalidRequestError(str(error)) from error
    except Exception as error:
        raise PipelineFailureError("Chat pipeline failed") from error


@router.get("/workspaces/{workspace_id}/chats", response_model=list[ChatSessionResponse])
def list_chats(workspace_id: str, storage: StorageDependency) -> list[ChatSessionResponse]:
    try:
        return [_chat_response(storage, chat) for chat in storage.list_chats(workspace_id)]
    except WorkspaceNotFound as error:
        raise InvalidRequestError(f"Workspace not found: {workspace_id}") from error


@router.get("/workspaces/{workspace_id}/chats/{chat_id}", response_model=ChatSessionResponse)
def get_chat(workspace_id: str, chat_id: str, storage: StorageDependency) -> ChatSessionResponse:
    try:
        chat = storage.get_chat(chat_id)
        if chat.workspace_id != workspace_id:
            raise ChatNotFound(chat_id)
        return _chat_response(storage, chat)
    except ChatNotFound as error:
        raise InvalidRequestError(f"Chat not found: {chat_id}") from error


@router.post("/workspaces/{workspace_id}/chats", response_model=ChatSessionResponse, status_code=201)
def create_chat(
    workspace_id: str,
    request: CreateChatRequest,
    storage: StorageDependency,
) -> ChatSessionResponse:
    try:
        chat = storage.create_chat(workspace_id, request.title)
        for message in request.messages:
            storage.save_chat_message(chat.chat_id, message.role, message.content)
        return _chat_response(storage, chat)
    except WorkspaceNotFound as error:
        raise InvalidRequestError(f"Workspace not found: {workspace_id}") from error


@router.delete("/workspaces/{workspace_id}/chats/{chat_id}", response_model=DeleteResponse)
def delete_chat(workspace_id: str, chat_id: str, storage: StorageDependency) -> DeleteResponse:
    try:
        chat = storage.get_chat(chat_id)
        if chat.workspace_id != workspace_id:
            raise ChatNotFound(chat_id)
        storage.delete_chat(chat_id)
        return DeleteResponse(success=True)
    except ChatNotFound as error:
        raise InvalidRequestError(f"Chat not found: {chat_id}") from error


@router.post(
    "/workspaces/{workspace_id}/chats/{chat_id}/messages",
    response_model=ChatSessionResponse,
)
def append_chat_message(
    workspace_id: str,
    chat_id: str,
    request: ChatMessageRequest,
    storage: StorageDependency,
) -> ChatSessionResponse:
    try:
        chat = storage.get_chat(chat_id)
        if chat.workspace_id != workspace_id:
            raise ChatNotFound(chat_id)
        storage.save_chat_message(chat_id, request.role, request.content)
        return _chat_response(storage, storage.get_chat(chat_id))
    except ChatNotFound as error:
        raise InvalidRequestError(f"Chat not found: {chat_id}") from error


def _chat_response(storage: StorageDependency, chat) -> ChatSessionResponse:
    return ChatSessionResponse(
        chat_id=chat.chat_id,
        workspace_id=chat.workspace_id,
        title=chat.title,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[
            ChatMessageResponse(
                message_id=message.message_id,
                chat_id=message.chat_id,
                role=message.role,
                content=message.content,
                timestamp=message.timestamp,
            )
            for message in storage.load_chat_history(chat.chat_id)
        ],
    )