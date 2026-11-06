"""API endpoints for repository ingestion, inspection, and file discovery."""

from typing import List
from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_repository_manager
from app.ingestion.manager import RepositoryManager
from app.schemas.repository import (
    RepositoryFilesResponse,
    RepositoryMetadata,
    RepositorySubmitRequest,
)

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.post(
    "",
    response_model=RepositoryMetadata,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a public GitHub repository",
)
async def ingest_repository(
    request: RepositorySubmitRequest,
    manager: RepositoryManager = Depends(get_repository_manager),
) -> RepositoryMetadata:
    """Clone, scan, and extract metadata from a public GitHub repository."""
    return await manager.ingest_repository(
        github_url=request.github_url,
        branch=request.branch,
    )


@router.get(
    "",
    response_model=List[RepositoryMetadata],
    summary="List all ingested repositories",
)
async def list_repositories(
    manager: RepositoryManager = Depends(get_repository_manager),
) -> List[RepositoryMetadata]:
    """Retrieve all previously ingested and indexed repositories."""
    return manager.list_repositories()


@router.get(
    "/{repository_id}",
    response_model=RepositoryMetadata,
    summary="Get repository metadata",
)
async def get_repository(
    repository_id: str,
    manager: RepositoryManager = Depends(get_repository_manager),
) -> RepositoryMetadata:
    """Retrieve metadata and ingestion summary for a specific repository."""
    return manager.get_repository(repository_id=repository_id)


@router.get(
    "/{repository_id}/files",
    response_model=RepositoryFilesResponse,
    summary="List discovered source and documentation files",
)
async def get_repository_files(
    repository_id: str,
    manager: RepositoryManager = Depends(get_repository_manager),
) -> RepositoryFilesResponse:
    """Retrieve the full list of discovered source code and documentation files."""
    return manager.get_repository_files(repository_id=repository_id)
