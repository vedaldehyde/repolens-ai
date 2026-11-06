"""High-level repository lifecycle manager coordinating cloning, scanning, caching, and persistence."""

import json
from pathlib import Path
from typing import List, Optional

from app.core.config import Settings, get_settings
from app.core.errors import NotFoundError, RepositoryError
from app.core.logging import get_logger
from app.ingestion.git_service import GitService
from app.ingestion.scanner import FileScanner
from app.schemas.repository import (
    DiscoveredFile,
    RepositoryFilesResponse,
    RepositoryMetadata,
    validate_and_parse_github_url,
)
from app.utils.path_helpers import sanitize_repo_id

logger = get_logger("app.ingestion.manager")


class RepositoryManager:
    """Manages cloning, scanning, idempotency, and persistence of ingested repositories."""

    def __init__(
        self,
        settings: Settings = get_settings(),
        git_service: Optional[GitService] = None,
        scanner: Optional[FileScanner] = None,
    ) -> None:
        self.settings = settings
        self.git_service = git_service or GitService(settings=settings)
        self.scanner = scanner or FileScanner(max_file_size_bytes=settings.MAX_FILE_SIZE_BYTES)

    def _get_repo_dir(self, repo_id: str) -> Path:
        """Get absolute path to repository directory within base repos directory."""
        return self.settings.absolute_repos_dir / repo_id

    def _get_metadata_file(self, repo_dir: Path) -> Path:
        return repo_dir / ".repolens" / "metadata.json"

    def _get_files_file(self, repo_dir: Path) -> Path:
        return repo_dir / ".repolens" / "files.json"

    async def ingest_repository(
        self,
        github_url: str,
        branch: Optional[str] = None,
        force_refresh: bool = False,
    ) -> RepositoryMetadata:
        """Ingest a public GitHub repository.

        Workflow:
        1. Validates and sanitizes GitHub URL against SSRF and syntax rules.
        2. Computes unique, deterministic repository ID.
        3. Checks for existing indexed repository (Idempotency).
        4. Safely shallow-clones the repo via Git CLI.
        5. Extracts commit SHA.
        6. Recursively scans repository for source code & docs.
        7. Persists metadata and discovered file contracts.
        """
        owner, repo, canonical_url = validate_and_parse_github_url(github_url)
        repo_id = sanitize_repo_id(owner, repo)
        target_dir = self._get_repo_dir(repo_id)
        metadata_file = self._get_metadata_file(target_dir)

        # Idempotency check: if already ingested and not forcing refresh, return existing
        if not force_refresh and metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                cached_meta = RepositoryMetadata(**cached_data)
                logger.info(f"Returning existing cached repository: {repo_id} (commit={cached_meta.commit_sha})")
                return cached_meta
            except Exception as e:
                logger.warning(f"Failed to read existing metadata for {repo_id}, re-cloning: {e}")

        # Execute safe Git clone
        commit_sha = await self.git_service.clone_repository(
            url=canonical_url,
            target_dir=target_dir,
            branch=branch,
        )

        # Scan repository files
        discovered_files, has_readme, readme_path, detected_languages = self.scanner.scan_directory(target_dir)
        total_size_bytes = sum(f.size_bytes for f in discovered_files)

        metadata = RepositoryMetadata(
            id=repo_id,
            name=repo,
            owner=owner,
            github_url=canonical_url,
            commit_sha=commit_sha,
            branch=branch,
            file_count=len(discovered_files),
            total_size_bytes=total_size_bytes,
            detected_languages=detected_languages,
            has_readme=has_readme,
            readme_path=readme_path,
            status="completed",
        )

        # Persist metadata and files index inside .repolens/ folder
        meta_dir = target_dir / ".repolens"
        meta_dir.mkdir(parents=True, exist_ok=True)

        with open(self._get_metadata_file(target_dir), "w", encoding="utf-8") as f:
            json.dump(metadata.model_dump(mode="json"), f, indent=2)

        with open(self._get_files_file(target_dir), "w", encoding="utf-8") as f:
            files_payload = [f.model_dump(mode="json") for f in discovered_files]
            json.dump(files_payload, f, indent=2)

        logger.info(f"Successfully ingested {repo_id}: {len(discovered_files)} files indexed")
        return metadata

    def get_repository(self, repository_id: str) -> RepositoryMetadata:
        """Fetch repository metadata by ID."""
        repo_dir = self._get_repo_dir(repository_id)
        metadata_file = self._get_metadata_file(repo_dir)

        if not metadata_file.exists():
            raise NotFoundError(f"Repository with ID '{repository_id}' not found.")

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return RepositoryMetadata(**data)
        except Exception as e:
            raise RepositoryError(f"Corrupted metadata for repository '{repository_id}': {str(e)}")

    def get_repository_files(self, repository_id: str) -> RepositoryFilesResponse:
        """Fetch list of all discovered files for a repository."""
        repo_dir = self._get_repo_dir(repository_id)
        files_file = self._get_files_file(repo_dir)

        if not files_file.exists():
            raise NotFoundError(f"Discovered files for repository '{repository_id}' not found.")

        try:
            with open(files_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            files = [DiscoveredFile(**item) for item in data]
            return RepositoryFilesResponse(
                repository_id=repository_id,
                file_count=len(files),
                files=files,
            )
        except Exception as e:
            raise RepositoryError(f"Corrupted files index for repository '{repository_id}': {str(e)}")

    def list_repositories(self) -> List[RepositoryMetadata]:
        """List all ingested repositories."""
        repos: List[RepositoryMetadata] = []
        base_dir = self.settings.absolute_repos_dir

        if not base_dir.exists():
            return repos

        for item in base_dir.iterdir():
            if item.is_dir():
                meta_file = self._get_metadata_file(item)
                if meta_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        repos.append(RepositoryMetadata(**data))
                    except Exception:
                        continue

        # Sort by ingested_at descending
        repos.sort(key=lambda r: r.ingested_at, reverse=True)
        return repos
