"""Health check API endpoints."""

from fastapi import APIRouter, Depends
from app.core.dependencies import get_health_service
from app.schemas.common import HealthStatusResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthStatusResponse, summary="System Health Status")
async def get_system_health(
    health_service: HealthService = Depends(get_health_service),
) -> HealthStatusResponse:
    """Return backend operational status, version, uptime, and diagnostics."""
    return health_service.check_health()
