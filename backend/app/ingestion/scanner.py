"""Source file discovery, binary filtering, and language identification."""

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from app.schemas.repository import DiscoveredFile

# Directories that must never be traversed
EXCLUDED_DIRECTORIES: Set[str] = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".env",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".idea",
    ".vscode",
    ".coverage",
    "htmlcov",
    ".gitattributes",
}

# Explicitly excluded binary/archive extensions
BINARY_EXTENSIONS: Set[str] = {
    ".pyc",
    ".pyd",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".bin",
    ".o",
    ".a",
    ".iso",
    ".tar",
    ".gz",
    ".zip",
    ".bz2",
    ".xz",
    ".7z",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".mp3",
    ".mp4",
    ".wav",
    ".avi",
    ".mov",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".wasm",
    ".min.js",
    ".min.css",
    ".map",
}

# Recognized file extension to language & category mapping
SUPPORTED_EXTENSIONS: Dict[str, Tuple[str, str]] = {
    # Python code
    ".py": ("Python", "code"),
    ".pyi": ("Python", "code"),
    # Documentation & markup
    ".md": ("Markdown", "documentation"),
    ".markdown": ("Markdown", "documentation"),
    ".rst": ("reStructuredText", "documentation"),
    ".txt": ("Text", "documentation"),
    # Configuration & manifest files
    ".toml": ("TOML", "configuration"),
    ".yaml": ("YAML", "configuration"),
    ".yml": ("YAML", "configuration"),
    ".json": ("JSON", "configuration"),
    ".ini": ("INI", "configuration"),
    ".cfg": ("Config", "configuration"),
}

# Known extensionless or special configuration files
SPECIAL_FILENAMES: Dict[str, Tuple[str, str]] = {
    "dockerfile": ("Dockerfile", "configuration"),
    "containerfile": ("Dockerfile", "configuration"),
    "makefile": ("Makefile", "configuration"),
    "gnumakefile": ("Makefile", "configuration"),
    "procfile": ("Procfile", "configuration"),
    "license": ("Text", "documentation"),
    "copying": ("Text", "documentation"),
}

README_FILENAMES: Set[str] = {
    "readme.md",
    "readme.rst",
    "readme.txt",
    "readme",
}


def is_binary_file(file_path: Path) -> bool:
    """Check if a file contains null bytes within its first 1024 bytes."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except Exception:
        return True


class FileScanner:
    """Recursively scans repository folders, filtering binaries and discovering source files."""

    def __init__(self, max_file_size_bytes: int = 500 * 1024) -> None:
        self.max_file_size_bytes = max_file_size_bytes

    def scan_directory(self, root_dir: Path) -> Tuple[List[DiscoveredFile], bool, Optional[str], List[str]]:
        """Scan a repository directory and return:

        - List of DiscoveredFile objects
        - has_readme (bool)
        - readme_path (str | None)
        - detected_languages (List[str] ordered by frequency)
        """
        discovered_files: List[DiscoveredFile] = []
        has_readme = False
        readme_path: Optional[str] = None
        language_counts: Dict[str, int] = {}

        for path in root_dir.rglob("*"):
            # Check if any parent directory is in EXCLUDED_DIRECTORIES
            parts = path.relative_to(root_dir).parts
            if any(part in EXCLUDED_DIRECTORIES or part.startswith(".") and part != "." for part in parts[:-1]):
                continue

            if not path.is_file():
                continue

            # Symlink guard: do not follow symlinks pointing outside root_dir
            try:
                resolved = path.resolve()
                if not str(resolved).startswith(str(root_dir.resolve())):
                    continue
            except Exception:
                continue

            filename_lower = path.name.lower()

            # Ignore hidden files like .gitignore or .DS_Store
            if path.name.startswith("."):
                continue

            # Ignore known binary files
            if any(filename_lower.endswith(ext) for ext in BINARY_EXTENSIONS):
                continue

            # Determine language & category
            ext = path.suffix.lower()
            lang_info = SUPPORTED_EXTENSIONS.get(ext)

            if not lang_info:
                # Check for special filenames without extensions (e.g. Dockerfile, Makefile)
                lang_info = SPECIAL_FILENAMES.get(filename_lower)

            if not lang_info:
                # Unsupported extension in initial Phase 2
                continue

            language, category = lang_info

            # Check file size limit
            try:
                file_size = path.stat().st_size
            except OSError:
                continue

            if file_size > self.max_file_size_bytes:
                # Exceeds size limit
                continue

            # Binary heuristic check
            if is_binary_file(path):
                continue

            rel_path = path.relative_to(root_dir).as_posix()

            # Check if this file is a README
            if filename_lower in README_FILENAMES and (not has_readme or len(parts) == 1):
                has_readme = True
                readme_path = rel_path

            discovered_files.append(
                DiscoveredFile(
                    path=rel_path,
                    size_bytes=file_size,
                    extension=ext if ext else path.name,
                    language=language,
                    category=category,
                )
            )

            language_counts[language] = language_counts.get(language, 0) + 1

        # Sort files by path for deterministic output
        discovered_files.sort(key=lambda f: f.path)

        # Sort detected languages by frequency descending
        sorted_languages = [
            lang
            for lang, _ in sorted(language_counts.items(), key=lambda item: item[1], reverse=True)
        ]

        return discovered_files, has_readme, readme_path, sorted_languages
