"""FastAPI application entry point for Retriev."""

import logging
import os
from time import perf_counter
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR / "server" / ".env", override=False)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from server.api.routes import chat, documents, health, ingestion, workspaces
from server.api.schemas.errors import (
    DocumentUploadFailureError,
    DocumentNotFoundError,
    InvalidRequestError,
    PipelineFailureError,
    WorkspaceNotFoundError,
    document_upload_failure_handler,
    document_not_found_handler,
    invalid_request_handler,
    pipeline_failure_handler,
    workspace_not_found_handler,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Retriev API",
    version="1.0.0",
    description="Retriev Local-first RAG Backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173","http://tauri.localhost",
        "tauri://localhost",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(WorkspaceNotFoundError, workspace_not_found_handler)
app.add_exception_handler(InvalidRequestError, invalid_request_handler)
app.add_exception_handler(PipelineFailureError, pipeline_failure_handler)
app.add_exception_handler(DocumentUploadFailureError, document_upload_failure_handler)
app.add_exception_handler(DocumentNotFoundError, document_not_found_handler)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = perf_counter()
    response = await call_next(request)
    logger.info(
        "%s %s | Status: %d | Time: %.2f ms",
        request.method,
        request.url.path,
        response.status_code,
        (perf_counter() - started) * 1000,
    )
    return response


app.include_router(health.router, prefix="/api")
app.include_router(workspaces.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(ingestion.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=int(os.getenv("RETRIEV_PORT", "8000")),
        reload=False,
    )