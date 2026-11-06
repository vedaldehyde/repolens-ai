"""Root API router consolidating all domain endpoints."""

from fastapi import APIRouter
from app.api.routes import health

api_router = APIRouter(prefix="/api")

# Register domain routes
api_router.include_router(health.router)
