"""FastAPI dependency injection providers."""

from app.core.config import Settings, get_settings
from app.ingestion.manager import RepositoryManager
from app.services.health_service import HealthService


def get_app_settings() -> Settings:
    """Dependency provider for cached application settings."""
    return get_settings()


def get_health_service() -> HealthService:
    """Dependency provider for the HealthService."""
    return HealthService()


def get_repository_manager() -> RepositoryManager:
    """Dependency provider for RepositoryManager."""
    return RepositoryManager()
