import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile

from server.api.dependencies import StorageDependency
from server.api.schemas.errors import (
    DocumentNotFoundError,
    DocumentUploadFailureError,
    WorkspaceNotFoundError,
)
from server.api.schemas.responses import (
    DocumentDeleteResponse,
    DocumentPreviewResponse,
    DocumentResponse,
    NativeImportFileResult,
    NativeImportRequest,
    NativeImportResponse,
)
from server.services.ingestion import ExtractionService
from server.services.storage.exceptions import WorkspaceNotFound

router = APIRouter(prefix="/workspaces/{workspace_id}/documents", tags=["documents"])
SUPPORTED_EXTENSIONS = {"pdf", "txt", "md", "csv", "docx"}


def _documents_path(storage: StorageDependency, workspace_id: str) -> Path:
    try:
        return Path(storage.get_workspace(workspace_id).path) / "docs"
    except WorkspaceNotFound as error:
        raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}") from error


def _document_path(storage: StorageDependency, workspace_id: str, file_name: str) -> Path:
    docs_path = _documents_path(storage, workspace_id).resolve()
    candidate = (docs_path / Path(file_name).name).resolve()
    if Path(file_name).name != file_name or candidate.parent != docs_path:
        raise DocumentNotFoundError(f"Document not found: {file_name}")
    if not candidate.is_file():
        raise DocumentNotFoundError(f"Document not found: {file_name}")
    return candidate


def _import_candidates(paths: list[str]) -> list[Path]:
    candidates: list[Path] = []
    for raw_path in paths:
        source = Path(raw_path).expanduser()
        if source.is_file():
            candidates.append(source)
        elif source.is_dir():
            candidates.extend(path for path in source.rglob("*") if path.is_file())
    return candidates


@router.post("/import", response_model=NativeImportResponse)
def import_documents(
    workspace_id: str,
    request: NativeImportRequest,
    storage: StorageDependency,
) -> NativeImportResponse:
    docs_path = _documents_path(storage, workspace_id)
    docs_path.mkdir(parents=True, exist_ok=True)
    results: list[NativeImportFileResult] = []
    imported = skipped = failed = 0
    missing_paths = {
        str(Path(raw_path).expanduser())
        for raw_path in request.paths
        if not Path(raw_path).expanduser().exists()
    }
    for source_path in sorted(missing_paths):
        failed += 1
        results.append(
            NativeImportFileResult(
                source_path=source_path,
                status="failed",
                detail="Source path does not exist or is inaccessible",
            )
        )
    for source in _import_candidates(request.paths):
        source_path = str(source)
        extension = source.suffix.lower().lstrip(".")
        if extension not in SUPPORTED_EXTENSIONS:
            skipped += 1
            results.append(
                NativeImportFileResult(
                    source_path=source_path,
                    file_name=source.name,
                    status="skipped",
                    detail="Unsupported file type",
                )
            )
            continue
        try:
            resolved_source = source.resolve()
            if resolved_source.parent == docs_path.resolve() and resolved_source != (docs_path / source.name).resolve():
                raise OSError("Source path could not be resolved safely")
            destination = docs_path / source.name
            shutil.copy2(resolved_source, destination)
            storage.remove_document_state(workspace_id, source.name)
            imported += 1
            results.append(
                NativeImportFileResult(
                    source_path=source_path,
                    file_name=source.name,
                    status="imported",
                )
            )
        except (OSError, ValueError) as error:
            failed += 1
            results.append(
                NativeImportFileResult(
                    source_path=source_path,
                    file_name=source.name,
                    status="failed",
                    detail=str(error),
                )
            )
    return NativeImportResponse(
        workspace_id=workspace_id,
        imported=imported,
        skipped=skipped,
        failed=failed,
        files=results,
    )


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    workspace_id: str, storage: StorageDependency
) -> list[DocumentResponse]:
    docs_path = _documents_path(storage, workspace_id)
    if not docs_path.exists():
        return []
    states = storage.list_document_states(workspace_id)
    return [
        DocumentResponse(
            file_name=file.name,
            file_type=file.suffix.lower().lstrip("."),
            size_bytes=file.stat().st_size,
            status="indexed" if states.get(file.name) else "uploaded",
        )
        for file in sorted(docs_path.iterdir())
        if file.is_file()
    ]


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    workspace_id: str,
    file: UploadFile,
    storage: StorageDependency,
) -> DocumentResponse:
    docs_path = _documents_path(storage, workspace_id)
    extension = Path(file.filename or "").suffix.lower().lstrip(".")
    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentUploadFailureError(
            f"Unsupported file type. Accepted types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    safe_name = Path(file.filename or "").name
    if not safe_name:
        raise DocumentUploadFailureError("Uploaded file must have a name")
    try:
        docs_path.mkdir(parents=True, exist_ok=True)
        destination = docs_path / safe_name
        content = await file.read()
        destination.write_bytes(content)
        return DocumentResponse(
            file_name=safe_name,
            file_type=extension,
            size_bytes=len(content),
            status="uploaded",
        )
    except OSError as error:
        raise DocumentUploadFailureError("Unable to save uploaded document") from error


@router.delete("/{file_name}", response_model=DocumentDeleteResponse)
def delete_document(
    workspace_id: str,
    file_name: str,
    storage: StorageDependency,
) -> DocumentDeleteResponse:
    document_path = _document_path(storage, workspace_id, file_name)
    document_path.unlink()
    storage.remove_document_state(workspace_id, file_name)
    return DocumentDeleteResponse(success=True, file_name=file_name)


@router.get("/{file_name}/content", response_model=DocumentPreviewResponse)
def preview_document(
    workspace_id: str,
    file_name: str,
    storage: StorageDependency,
) -> DocumentPreviewResponse:
    document_path = _document_path(storage, workspace_id, file_name)
    try:
        extracted = ExtractionService.extract(document_path)
    except Exception as error:
        raise DocumentUploadFailureError("Unable to preview document") from error
    preview = "\n\n".join(unit.content for unit in extracted.units)[:3000]
    return DocumentPreviewResponse(
        file_name=extracted.file_name,
        preview=preview,
        file_type=extracted.file_type,
    )
