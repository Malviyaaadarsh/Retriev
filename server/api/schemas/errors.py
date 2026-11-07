"""Exceptions and handlers for API errors."""

from fastapi import Request
from fastapi.responses import JSONResponse


class WorkspaceNotFoundError(Exception):
    """The requested workspace does not exist."""


class InvalidRequestError(Exception):
    """The request cannot be processed."""


class PipelineFailureError(Exception):
    """A pipeline failed while handling a request."""


class DocumentUploadFailureError(Exception):
    """A document could not be saved."""


class DocumentNotFoundError(Exception):
    """The requested document does not exist."""


async def workspace_not_found_handler(
    request: Request, error: WorkspaceNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})


async def invalid_request_handler(
    request: Request, error: InvalidRequestError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(error)})


async def pipeline_failure_handler(
    request: Request, error: PipelineFailureError
) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(error)})


async def document_upload_failure_handler(
    request: Request, error: DocumentUploadFailureError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(error)})


async def document_not_found_handler(
    request: Request, error: DocumentNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})
