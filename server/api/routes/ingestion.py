from fastapi import APIRouter

from server.api.dependencies import IngestionDependency, StorageDependency
from server.api.schemas.errors import PipelineFailureError, WorkspaceNotFoundError
from server.api.schemas.responses import IngestionResponse
from server.services.storage.exceptions import WorkspaceNotFound

router = APIRouter(prefix="/workspaces/{workspace_id}", tags=["ingestion"])


@router.post("/ingest", response_model=IngestionResponse)
def ingest_workspace(
    workspace_id: str,
    storage: StorageDependency,
    pipeline: IngestionDependency,
) -> IngestionResponse:
    try:
        workspace = storage.get_workspace(workspace_id)
    except WorkspaceNotFound as error:
        raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}") from error
    try:
        result = pipeline.run(workspace_id, workspace.path)
        for report in result.reports:
            if report.status == "success":
                storage.mark_document_indexed(workspace_id, report.file_name)
        return IngestionResponse(
            workspace_id=result.workspace_id,
            success=result.success,
            files_processed=result.files_processed,
            files_failed=result.files_failed,
            chunks_generated=result.chunks_generated,
            embeddings_generated=result.embeddings_generated,
            vectors_stored=result.vectors_stored,
            documents_indexed=result.documents_indexed,
            total_time_seconds=result.total_time_seconds,
        )
    except Exception as error:
        raise PipelineFailureError("Ingestion pipeline failed") from error
