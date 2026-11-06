"""Standardized API response models and health schema."""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class HealthStatusResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(default="healthy", description="Operational status: healthy, degraded, or unhealthy")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Current UTC timestamp",
    )
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Active environment name")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="System component diagnostics (memory, storage, etc.)",
    )


class ApiResponse(BaseModel, Generic[DataT]):
    """Standard success response wrapper."""

    success: bool = Field(default=True, description="Indicates request success")
    message: Optional[str] = Field(default=None, description="Human readable status message")
    data: Optional[DataT] = Field(default=None, description="Payload data")


class ErrorDetail(BaseModel):
    """Structured error payload schema."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context or validation details")


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = Field(default=False, description="Always false for error envelopes")
    error: ErrorDetail = Field(..., description="Detailed error information")
