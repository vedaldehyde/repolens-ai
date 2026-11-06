"""Repository ingestion contracts and interfaces.

Scaffolding for Phase 2: Git CLI cloning, shallow clone, shallow fetch,
and repository lifecycle management.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from app.schemas.repository import RepositoryMetadata


class BaseRepositoryIngestionService(ABC):
    """Abstract interface for repository cloning and lifecycle management."""

    @abstractmethod
    async def clone_repository(self, url: str, branch: Optional[str] = None) -> Path:
        """Clone a remote repository to the local data directory.

        Implementation deferred to Phase 2.
        """
        pass

    @abstractmethod
    async def cleanup_repository(self, repo_id: str) -> bool:
        """Remove local cloned repository data.

        Implementation deferred to Phase 2.
        """
        pass

    @abstractmethod
    async def get_repository_metadata(self, repo_path: Path) -> RepositoryMetadata:
        """Extract git metadata and repository summary statistics.

        Implementation deferred to Phase 2.
        """
        pass
