"""Pytest configuration and test fixtures."""

from typing import Generator
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_application


def get_test_settings() -> Settings:
    """Provide isolated settings for testing."""
    return Settings(
        ENVIRONMENT="development",
        DEBUG=True,
        CORS_ORIGINS=["http://localhost:5173", "http://testserver"],
        DATA_DIR="test_data",
        REPOS_DIR="test_data/repos",
        CHROMA_PERSIST_DIR="test_data/chroma",
    )


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """TestClient fixture initialized with FastAPI application."""
    app = create_application()
    app.dependency_overrides[get_settings] = get_test_settings
    with TestClient(app) as test_client:
        yield test_client
