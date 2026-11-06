"""Repository ingestion schemas and data contracts."""

import re
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

GITHUB_URL_PATTERN = re.compile(r"^https://github\.com/[\w\.-]+/[\w\.-]+/?$")


class RepositorySubmitRequest(BaseModel):
    """Schema for repository submission."""

    url: str = Field(..., description="Public GitHub repository URL (e.g., https://github.com/psf/requests)")
    branch: Optional[str] = Field(default=None, description="Optional branch or tag to clone")

    @field_validator("url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        clean_url = v.strip().rstrip("/")
        if not GITHUB_URL_PATTERN.match(clean_url):
            raise ValueError("URL must be a valid public GitHub repository URL (e.g. https://github.com/owner/repo)")
        return clean_url


class RepositoryMetadata(BaseModel):
    """Metadata representing an indexed repository."""

    id: str = Field(..., description="Unique repository identifier")
    owner: str = Field(..., description="Repository owner or organization")
    name: str = Field(..., description="Repository name")
    url: str = Field(..., description="Canonical repository URL")
    default_branch: str = Field(default="main", description="Target branch")
    total_files: int = Field(default=0, description="Total source files indexed")
    total_symbols: int = Field(default=0, description="Total functions, classes, and symbols parsed")
    indexed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Index creation timestamp",
    )
    supported_languages: List[str] = Field(
        default_factory=lambda: ["python"],
        description="List of detected programming languages",
    )
