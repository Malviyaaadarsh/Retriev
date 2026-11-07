from fastapi import APIRouter

from fastapi import HTTPException

from server.api.dependencies import StorageDependency, check_readiness
from server.api.schemas.responses import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(storage: StorageDependency) -> HealthResponse:
    checks = storage.health_check()
    return HealthResponse(
        status="healthy" if all(checks.values()) else "degraded",
        sqlite=checks["sqlite"],
        lancedb=checks["lancedb"],
        version="1.0.0",
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness() -> ReadinessResponse:
    checks = check_readiness()
    ready = bool(
        checks["sqlite"] and checks["lancedb"] and checks["embedding_model"]
    )
    response = ReadinessResponse(
        status="ready" if ready else "not_ready",
        sqlite=bool(checks["sqlite"]),
        lancedb=bool(checks["lancedb"]),
        embedding_model=bool(checks["embedding_model"]),
        detail=checks["detail"] if isinstance(checks["detail"], str) else None,
        version="1.0.0",
    )
    if not ready:
        raise HTTPException(status_code=503, detail=response.model_dump())
    return response
