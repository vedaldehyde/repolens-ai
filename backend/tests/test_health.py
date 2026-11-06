"""Tests for API health endpoints, CORS, configuration, and error handlers."""

from fastapi.testclient import TestClient
from app.core.config import Settings
from app.utils.path_helpers import resolve_safe_path, sanitize_repo_id
import pytest


def test_health_endpoint_returns_200(client: TestClient) -> None:
    """Verify GET /api/health returns HTTP 200 with required schema fields."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], (int, float))
    assert "details" in data
    assert "storage" in data["details"]


def test_cors_headers_on_health_endpoint(client: TestClient) -> None:
    """Verify CORS allowlist properly returns Access-Control-Allow-Origin."""
    response = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_rejects_unlisted_origin(client: TestClient) -> None:
    """Verify unlisted origins do not receive allow-origin header."""
    response = client.get(
        "/api/health",
        headers={"Origin": "http://malicious-site.com"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_centralized_not_found_envelope(client: TestClient) -> None:
    """Verify 404 responses conform to centralized error schema."""
    response = client.get("/api/non-existent-endpoint")
    assert response.status_code == 404
    data = response.json()

    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
    assert "message" in data["error"]


def test_cors_origins_validator_handles_strings_and_lists() -> None:
    """Verify CORS_ORIGINS parser handles comma-separated strings and JSON arrays."""
    s1 = Settings(CORS_ORIGINS="http://localhost:3000, http://example.com")
    assert s1.CORS_ORIGINS == ["http://localhost:3000", "http://example.com"]

    s2 = Settings(CORS_ORIGINS='["http://alpha.com", "http://beta.com"]')
    assert s2.CORS_ORIGINS == ["http://alpha.com", "http://beta.com"]


def test_path_helpers() -> None:
    """Verify repository ID sanitization and path traversal guard."""
    sanitized = sanitize_repo_id("langchain-ai", "langgraph")
    assert sanitized == "langchain-ai__langgraph"

    sanitized_special = sanitize_repo_id("user/../hacker", "repo$name")
    assert ".." not in sanitized_special

    from pathlib import Path
    base = Path("/tmp/repolens_test").resolve()
    safe = resolve_safe_path(base, "valid/subfolder")
    assert str(safe).startswith(str(base))

    with pytest.raises(ValueError, match="Path traversal"):
        resolve_safe_path(base, "../../etc/passwd")
