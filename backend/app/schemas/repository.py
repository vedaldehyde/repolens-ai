"""Repository ingestion schemas and data contracts."""

from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse
import re

from pydantic import BaseModel, Field, model_validator


GITHUB_URL_REGEX = re.compile(r"^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?/?$")
NAME_CLEAN_REGEX = re.compile(r"^[a-zA-Z0-9_.-]+$")


def validate_and_parse_github_url(raw_url: str) -> tuple[str, str, str]:
    """Validate a public GitHub URL against SSRF and extract (owner, repo, canonical_url).

    Guarantees:
    - Protocol is https only.
    - Hostname is github.com only.
    - No embedded credentials (user:pass@).
    - No port specifications.
    - Path strictly adheres to /owner/repo.
    - Traversal characters ('..') and invalid naming patterns are rejected.
    """
    clean_url = raw_url.strip()
    if not clean_url:
        raise ValueError("GitHub URL cannot be empty")

    parsed = urlparse(clean_url)

    if parsed.scheme.lower() != "https":
        raise ValueError("Only secure HTTPS URLs are supported (e.g. https://github.com/owner/repo)")

    if parsed.hostname is None or parsed.hostname.lower() != "github.com":
        raise ValueError("Repository URL must be hosted on github.com")

    if parsed.username or parsed.password:
        raise ValueError("URL must not contain embedded authentication credentials")

    if parsed.port and parsed.port != 443:
        raise ValueError("Custom ports are not permitted for security reasons")

    if parsed.query or parsed.fragment:
        raise ValueError("URL must not contain query parameters or URL fragments")

    match = GITHUB_URL_REGEX.match(clean_url)
    if not match:
        raise ValueError(
            "Invalid GitHub URL structure. Expected format: https://github.com/owner/repository"
        )

    owner, repo = match.group(1), match.group(2)

    # Validate owner & repo naming to block any path traversal
    if ".." in owner or ".." in repo:
        raise ValueError("Invalid repository or owner name: directory traversal sequence detected")

    if not NAME_CLEAN_REGEX.match(owner) or not NAME_CLEAN_REGEX.match(repo):
        raise ValueError("Owner and repository names can only contain alphanumeric characters, '.', '_', and '-'")

    if owner.startswith(".") or repo.startswith("."):
        raise ValueError("Owner and repository names cannot start with a dot")

    canonical_url = f"https://github.com/{owner}/{repo}"
    return owner, repo, canonical_url


class RepositorySubmitRequest(BaseModel):
    """Schema for repository submission."""

    github_url: str = Field(
        ...,
        description="Public GitHub repository URL (e.g., https://github.com/psf/requests)",
    )
    branch: Optional[str] = Field(default=None, description="Optional branch or tag to clone")

    @model_validator(mode="before")
    @classmethod
    def handle_url_alias_and_validate(cls, data: object) -> object:
        if isinstance(data, dict):
            # Support both 'github_url' and 'url'
            url = data.get("github_url") or data.get("url")
            if not url:
                raise ValueError("Field 'github_url' is required")
            # Validate format
            _, _, canonical = validate_and_parse_github_url(str(url))
            data["github_url"] = canonical
        return data


class DiscoveredFile(BaseModel):
    """Represents a discovered and scanned file in the repository."""

    path: str = Field(..., description="Repository-relative file path (forward slashes)")
    size_bytes: int = Field(..., description="File size in bytes")
    extension: str = Field(..., description="File extension with leading dot (e.g. .py)")
    language: str = Field(..., description="Detected programming or markup language")
    category: str = Field(..., description="File category: code, documentation, configuration")


class RepositoryMetadata(BaseModel):
    """Metadata representing an ingested and indexed repository."""

    id: str = Field(..., description="Unique repository identifier")
    name: str = Field(..., description="Repository name")
    owner: str = Field(..., description="Repository owner or organization")
    github_url: str = Field(..., description="Canonical GitHub repository URL")
    commit_sha: str = Field(..., description="Exact 40-character Git commit SHA analyzed")
    branch: Optional[str] = Field(default=None, description="Cloned Git branch or tag name")
    file_count: int = Field(default=0, description="Total source and documentation files discovered")
    total_size_bytes: int = Field(default=0, description="Total size in bytes of scanned files")
    detected_languages: List[str] = Field(
        default_factory=list,
        description="List of detected programming/doc languages in order of prominence",
    )
    has_readme: bool = Field(default=False, description="Whether a top-level README file exists")
    readme_path: Optional[str] = Field(default=None, description="Relative path to project README")
    ingested_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when repository was ingested",
    )
    status: str = Field(default="completed", description="Ingestion status: completed, processing, failed")


class RepositoryFilesResponse(BaseModel):
    """List of files discovered within an ingested repository."""

    repository_id: str = Field(..., description="Unique repository identifier")
    file_count: int = Field(..., description="Total files returned")
    files: List[DiscoveredFile] = Field(default_factory=list, description="List of discovered files")
