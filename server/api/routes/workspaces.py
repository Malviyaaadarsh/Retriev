from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter
from server.path import APP_PATHS
from server.api.dependencies import StorageDependency
from server.api.schemas.errors import WorkspaceNotFoundError
from server.api.schemas.requests import CreateWorkspaceRequest
from server.api.schemas.responses import DeleteResponse, WorkspaceResponse
from server.services.storage.exceptions import WorkspaceNotFound

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=201)
def create_workspace(
    request: CreateWorkspaceRequest,
    storage: StorageDependency,
) -> WorkspaceResponse:
    workspace_id = str(uuid4())
    path = APP_PATHS.workspace_dir / workspace_id
    (path / "docs").mkdir(parents=True, exist_ok=True)
    workspace = storage.create_workspace(request.name, str(path), workspace_id)
    return WorkspaceResponse.model_validate(workspace)


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(storage: StorageDependency) -> list[WorkspaceResponse]:
    return [WorkspaceResponse.model_validate(item) for item in storage.list_workspaces()]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(workspace_id: str, storage: StorageDependency) -> WorkspaceResponse:
    try:
        return WorkspaceResponse.model_validate(storage.get_workspace(workspace_id))
    except WorkspaceNotFound as error:
        raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}") from error


@router.delete("/{workspace_id}", response_model=DeleteResponse)
def delete_workspace(workspace_id: str, storage: StorageDependency) -> DeleteResponse:
    try:
        workspace = storage.get_workspace(workspace_id)
        storage.delete_workspace(workspace_id)
        workspace_path = Path(workspace.path)
        if workspace_path.exists():
            import shutil

            shutil.rmtree(workspace_path)
        return DeleteResponse(success=True)
    except WorkspaceNotFound as error:
        raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}") from error
