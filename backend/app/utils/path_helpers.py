"""Path utilities and security helpers for filesystem operations."""

from pathlib import Path
import re


def sanitize_repo_id(owner: str, name: str) -> str:
    """Create a filesystem-safe identifier for a cloned repository.

    Strips any traversal characters (e.g. '..', '/', '\\') and special symbols,
    leaving only alphanumeric characters, underscores, and hyphens.
    """
    clean_owner = re.sub(r"\.+", "_", owner.strip())
    clean_name = re.sub(r"\.+", "_", name.strip())
    sanitized_owner = re.sub(r"[^\w\-]", "_", clean_owner)
    sanitized_name = re.sub(r"[^\w\-]", "_", clean_name)
    return f"{sanitized_owner}__{sanitized_name}"


def resolve_safe_path(base_dir: Path, target_path: str) -> Path:
    """Resolve a target path securely within base_dir, guarding against path traversal attacks."""
    resolved_base = base_dir.resolve()
    resolved_target = (resolved_base / target_path).resolve()

    if not str(resolved_target).startswith(str(resolved_base)):
        raise ValueError(f"Path traversal detected: {target_path} is outside {resolved_base}")

    return resolved_target
