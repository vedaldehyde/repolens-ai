"""Application configuration settings for RepoLens AI backend.

Validates environment variables using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Union
import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration with strict validation."""

    # Project metadata
    PROJECT_NAME: str = Field(default="RepoLens AI", description="Application display name")
    VERSION: str = Field(default="0.1.0", description="Application semantic version")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Debug mode toggle")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Network configuration
    HOST: str = Field(default="0.0.0.0", description="Backend host binding")
    PORT: int = Field(default=8000, description="Backend port binding")

    # Explicit CORS Allowlist
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Explicit list of permitted CORS origins",
    )

    # Storage paths (relative to backend or absolute)
    DATA_DIR: str = Field(default="data", description="Base data directory")
    REPOS_DIR: str = Field(default="data/repos", description="Directory to store cloned repositories")
    CHROMA_PERSIST_DIR: str = Field(default="data/chroma", description="ChromaDB persistence folder")

    # Ingestion & Git Security Limits (Phase 2)
    CLONE_TIMEOUT_SECONDS: int = Field(default=60, description="Git clone timeout in seconds")
    MAX_REPO_SIZE_MB: int = Field(default=150, description="Maximum allowed repository disk size in megabytes")
    MAX_FILE_SIZE_BYTES: int = Field(default=500 * 1024, description="Maximum single file size to scan (500 KB)")
    ALLOWED_GIT_HOSTS: List[str] = Field(default=["github.com"], description="Whitelisted Git hosting domains")

    # LLM & AI Engine settings (Configurable for Phase 3+)
    GROQ_API_KEY: str = Field(default="", description="Groq API Key")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Groq model ID")
    EMBEDDING_MODEL_NAME: str = Field(default="all-MiniLM-L6-v2", description="SentenceTransformers model name")

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from JSON list, comma-separated string, or list."""
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value.startswith("[") and value.endswith("]"):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if item]
                except json.JSONDecodeError:
                    pass
            # Fallback to comma-separated values
            return [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, (list, tuple)):
            return [str(item).strip() for item in value if item]
        return []

    @property
    def is_production(self) -> bool:
        """Helper to check if current environment is production."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def base_dir(self) -> Path:
        """Root backend directory path."""
        return Path(__file__).resolve().parent.parent.parent

    @property
    def absolute_repos_dir(self) -> Path:
        """Resolved absolute path for repositories storage."""
        path = Path(self.REPOS_DIR)
        return path if path.is_absolute() else self.base_dir / path

    @property
    def absolute_chroma_dir(self) -> Path:
        """Resolved absolute path for ChromaDB storage."""
        path = Path(self.CHROMA_PERSIST_DIR)
        return path if path.is_absolute() else self.base_dir / path


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
