"""Tests for repository ingestion, Git CLI subprocess security, scanning, and API endpoints."""

import os
import subprocess
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.ingestion.manager import RepositoryManager
from app.ingestion.scanner import FileScanner, is_binary_file
from app.schemas.repository import validate_and_parse_github_url


# ---------------------------------------------------------------------------
# 1. URL Validation and SSRF Prevention Tests
# ---------------------------------------------------------------------------

def test_url_validation_valid_cases() -> None:
    valid_urls = [
        "https://github.com/psf/requests",
        "https://github.com/psf/requests.git",
        "https://github.com/psf/requests/",
        "https://github.com/tiangolo/fastapi",
        "https://github.com/langchain-ai/langgraph",
    ]
    for url in valid_urls:
        owner, repo, canonical = validate_and_parse_github_url(url)
        assert owner
        assert repo
        assert canonical.startswith("https://github.com/")


def test_url_validation_rejects_ssrf_and_invalid() -> None:
    invalid_urls = [
        "http://github.com/owner/repo",                  # Non-https
        "git://github.com/owner/repo",                   # Non-https protocol
        "ssh://git@github.com/owner/repo",               # SSH protocol
        "file:///etc/passwd",                            # File protocol
        "https://127.0.0.1/owner/repo",                  # Loopback IP
        "https://169.254.169.254/latest/meta-data",      # Cloud metadata SSRF
        "https://localhost/owner/repo",                  # Localhost
        "https://gitlab.com/owner/repo",                 # Non-GitHub host
        "https://user:password@github.com/owner/repo",   # Embedded credentials
        "https://github.com:8443/owner/repo",            # Non-standard port
        "https://github.com/../evil/repo",               # Directory traversal in owner
        "https://github.com/owner/..",                   # Directory traversal in repo
        "https://github.com/owner/repo?param=value",     # Query parameter
        "https://github.com/owner/repo#heading",         # URL fragment
    ]
    for url in invalid_urls:
        with pytest.raises(ValueError):
            validate_and_parse_github_url(url)


# ---------------------------------------------------------------------------
# 2. FileScanner & Binary Filtering Tests
# ---------------------------------------------------------------------------

def test_scanner_discovers_source_and_filters_binaries(tmp_path: Path) -> None:
    # Setup test workspace hierarchy
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    # Valid files
    (repo_dir / "main.py").write_text("print('hello world')", encoding="utf-8")
    (repo_dir / "README.md").write_text("# Test Repo", encoding="utf-8")
    (repo_dir / "pyproject.toml").write_text("[tool.poetry]", encoding="utf-8")
    (repo_dir / "Dockerfile").write_text("FROM python:3.11", encoding="utf-8")

    sub_dir = repo_dir / "src"
    sub_dir.mkdir()
    (sub_dir / "utils.py").write_text("def add(a, b): return a + b", encoding="utf-8")

    # Excluded directories
    git_dir = repo_dir / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("dummy", encoding="utf-8")

    node_dir = repo_dir / "node_modules" / "package"
    node_dir.mkdir(parents=True)
    (node_dir / "index.js").write_text("console.log()", encoding="utf-8")

    venv_dir = repo_dir / ".venv" / "lib"
    venv_dir.mkdir(parents=True)
    (venv_dir / "site.py").write_text("pass", encoding="utf-8")

    # Excluded binaries
    (repo_dir / "binary.so").write_bytes(b"\x7fELF\x00\x00")
    (repo_dir / "corrupted.py").write_bytes(b"some text\x00with null byte")

    # Excluded oversize file (scanner limit set to 1000 bytes)
    (repo_dir / "oversize.py").write_text("x" * 2000, encoding="utf-8")

    scanner = FileScanner(max_file_size_bytes=1000)
    discovered_files, has_readme, readme_path, detected_languages = scanner.scan_directory(repo_dir)

    paths = [f.path for f in discovered_files]
    assert "main.py" in paths
    assert "README.md" in paths
    assert "pyproject.toml" in paths
    assert "Dockerfile" in paths
    assert "src/utils.py" in paths

    # Assert excluded files are NOT discovered
    assert not any(".git" in p for p in paths)
    assert not any("node_modules" in p for p in paths)
    assert not any(".venv" in p for p in paths)
    assert "binary.so" not in paths
    assert "corrupted.py" not in paths
    assert "oversize.py" not in paths

    # Assert metadata
    assert has_readme is True
    assert readme_path == "README.md"
    assert "Python" in detected_languages
    assert "Markdown" in detected_languages


def test_is_binary_file_helper(tmp_path: Path) -> None:
    text_file = tmp_path / "hello.txt"
    text_file.write_text("Clean text without nulls")
    assert is_binary_file(text_file) is False

    bin_file = tmp_path / "nulls.bin"
    bin_file.write_bytes(b"header\x00data")
    assert is_binary_file(bin_file) is True


# ---------------------------------------------------------------------------
# 3. RepositoryManager and API Endpoints Integration Test
# ---------------------------------------------------------------------------

@pytest.fixture
def fixture_git_repo(tmp_path: Path) -> Path:
    """Creates a real local Git repository to serve as a clone fixture."""
    repo_dir = tmp_path / "fixture_source"
    repo_dir.mkdir()

    # Initialize Git repository
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "tester@test.com"], cwd=repo_dir, check=True)

    # Add source files
    (repo_dir / "README.md").write_text("# Fixture Repo\nExample description.", encoding="utf-8")
    (repo_dir / "calculator.py").write_text("def sum_vals(x, y):\n    return x + y\n", encoding="utf-8")

    # Add commit
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)

    return repo_dir


@pytest.mark.asyncio
async def test_repository_manager_end_to_end(tmp_path: Path, fixture_git_repo: Path) -> None:
    """Test cloning from fixture, scanning, persistence, and idempotency."""
    from app.core.config import Settings
    from app.ingestion.git_service import GitService

    settings = Settings(
        DATA_DIR=str(tmp_path / "data"),
        REPOS_DIR=str(tmp_path / "data" / "repos"),
        CHROMA_PERSIST_DIR=str(tmp_path / "data" / "chroma"),
    )

    git_service = GitService(settings=settings)

    # Mock clone_repository to clone from local fixture instead of hitting github.com over network
    async def mock_clone(url: str, target_dir: Path, branch=None) -> str:
        subprocess.run(
            ["git", "clone", "--depth", "1", str(fixture_git_repo), str(target_dir)],
            check=True,
            capture_output=True,
        )
        return await git_service.get_head_commit_sha(target_dir)

    git_service.clone_repository = mock_clone  # type: ignore[assignment]
    manager = RepositoryManager(settings=settings, git_service=git_service)

    # 1. Ingest repository
    meta = await manager.ingest_repository("https://github.com/fixture-owner/fixture-repo")
    assert meta.id == "fixture-owner__fixture-repo"
    assert meta.owner == "fixture-owner"
    assert meta.name == "fixture-repo"
    assert meta.file_count == 2
    assert meta.has_readme is True
    assert meta.readme_path == "README.md"
    assert len(meta.commit_sha) == 40
    assert "Python" in meta.detected_languages

    # 2. Test Idempotency: second call returns cached metadata without re-cloning
    second_meta = await manager.ingest_repository("https://github.com/fixture-owner/fixture-repo")
    assert second_meta.commit_sha == meta.commit_sha
    assert second_meta.file_count == meta.file_count

    # 3. Retrieve files
    files_resp = manager.get_repository_files(meta.id)
    assert files_resp.file_count == 2
    file_paths = [f.path for f in files_resp.files]
    assert "calculator.py" in file_paths
    assert "README.md" in file_paths

    # 4. Retrieve repository by ID
    fetched_meta = manager.get_repository(meta.id)
    assert fetched_meta.id == meta.id

    # 5. List repositories
    all_repos = manager.list_repositories()
    assert len(all_repos) == 1
    assert all_repos[0].id == meta.id


def test_api_repository_endpoints(client: TestClient, fixture_git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test POST /api/repositories, GET /api/repositories/{id}, and GET /api/repositories/{id}/files."""
    from app.core.dependencies import get_repository_manager
    from app.core.config import get_settings
    from app.ingestion.git_service import GitService

    settings = get_settings()
    git_service = GitService(settings=settings)

    async def mock_clone(url: str, target_dir: Path, branch=None) -> str:
        subprocess.run(
            ["git", "clone", "--depth", "1", str(fixture_git_repo), str(target_dir)],
            check=True,
            capture_output=True,
        )
        return await git_service.get_head_commit_sha(target_dir)

    git_service.clone_repository = mock_clone  # type: ignore[assignment]
    test_manager = RepositoryManager(settings=settings, git_service=git_service)

    client.app.dependency_overrides[get_repository_manager] = lambda: test_manager

    # 1. Test POST /api/repositories with invalid URL format
    res_bad = client.post("/api/repositories", json={"github_url": "http://malicious.com/owner/repo"})
    assert res_bad.status_code == 422
    assert res_bad.json()["success"] is False

    # 2. Test POST /api/repositories with valid URL
    res_post = client.post(
        "/api/repositories",
        json={"github_url": "https://github.com/test-org/calculator-service"},
    )
    assert res_post.status_code == 201
    data = res_post.json()
    assert data["id"] == "test-org__calculator-service"
    assert data["name"] == "calculator-service"
    assert data["owner"] == "test-org"
    assert data["file_count"] == 2
    assert data["has_readme"] is True

    repo_id = data["id"]

    # 3. Test GET /api/repositories/{id}
    res_get = client.get(f"/api/repositories/{repo_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == repo_id

    # 4. Test GET /api/repositories/{id}/files
    res_files = client.get(f"/api/repositories/{repo_id}/files")
    assert res_files.status_code == 200
    files_data = res_files.json()
    assert files_data["file_count"] == 2
    assert any(f["path"] == "calculator.py" for f in files_data["files"])

    # 5. Test GET /api/repositories/{id} not found
    res_404 = client.get("/api/repositories/non-existent-repo-id")
    assert res_404.status_code == 404
    assert res_404.json()["success"] is False
    assert res_404.json()["error"]["code"] == "NOT_FOUND"

    client.app.dependency_overrides.clear()
