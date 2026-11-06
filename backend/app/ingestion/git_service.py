"""Safe Git CLI subprocess wrapper for repository cloning and commit inspection."""

import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional

from app.core.config import Settings, get_settings
from app.core.errors import RepositoryError
from app.core.logging import get_logger

logger = get_logger("app.ingestion.git")


class GitService:
    """Encapsulates secure Git CLI execution without shell=True."""

    def __init__(self, settings: Settings = get_settings()) -> None:
        self.settings = settings

    def _get_hardened_env(self) -> Dict[str, str]:
        """Produce a restricted environment preventing interactive prompts and external leaks."""
        return {
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS": "echo",
            "GIT_CONFIG_NOSYSTEM": "1",
            "HOME": tempfile.gettempdir(),
            "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"),
        }

    async def clone_repository(
        self,
        url: str,
        target_dir: Path,
        branch: Optional[str] = None,
    ) -> str:
        """Execute a shallow, single-branch Git clone into target_dir and return the commit SHA.

        Safety guarantees:
        - shell=False strictly enforced.
        - HTTP redirect following disabled to guard against SSRF redirection.
        - Interactive terminal authentication disabled.
        - Strict timeout applied.
        - Code execution from downloaded repo is strictly prohibited.
        """
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        target_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "git",
            "-c", "protocol.allow=never",
            "-c", "protocol.https.allow=always",
            "-c", "http.followRedirects=false",
            "clone",
            "--depth", "1",
            "--single-branch",
        ]

        if branch:
            cmd.extend(["--branch", branch])

        cmd.extend([url, str(target_dir)])

        logger.info(f"Cloning repository: url={url}, branch={branch}, target={target_dir}")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._get_hardened_env(),
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.settings.CLONE_TIMEOUT_SECONDS,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                shutil.rmtree(target_dir, ignore_errors=True)
                raise RepositoryError(
                    f"Git clone timed out after {self.settings.CLONE_TIMEOUT_SECONDS} seconds"
                )

            if process.returncode != 0:
                stderr_text = stderr_bytes.decode("utf-8", errors="replace").strip()
                shutil.rmtree(target_dir, ignore_errors=True)
                logger.warning(f"Git clone returned error ({process.returncode}): {stderr_text}")

                if "could not read Username" in stderr_text or "Authentication failed" in stderr_text or "Repository not found" in stderr_text:
                    raise RepositoryError(
                        f"GitHub repository not found or is private: {url}"
                    )
                elif "Remote branch" in stderr_text and "not found" in stderr_text:
                    raise RepositoryError(
                        f"Specified branch or tag '{branch}' not found in repository"
                    )
                else:
                    raise RepositoryError(
                        f"Failed to clone repository: {stderr_text.splitlines()[-1] if stderr_text else 'Unknown git error'}"
                    )

            # Enforce repository size limit on disk
            repo_size_bytes = sum(f.stat().st_size for f in target_dir.rglob("*") if f.is_file())
            repo_size_mb = repo_size_bytes / (1024 * 1024)
            if repo_size_mb > self.settings.MAX_REPO_SIZE_MB:
                shutil.rmtree(target_dir, ignore_errors=True)
                raise RepositoryError(
                    f"Repository size ({repo_size_mb:.1f} MB) exceeds maximum allowed limit ({self.settings.MAX_REPO_SIZE_MB} MB)"
                )

            # Record exact commit SHA
            commit_sha = await self.get_head_commit_sha(target_dir)
            logger.info(f"Clone successful: commit_sha={commit_sha}, size={repo_size_mb:.2f} MB")
            return commit_sha

        except RepositoryError:
            raise
        except Exception as exc:
            shutil.rmtree(target_dir, ignore_errors=True)
            logger.exception(f"Unexpected error during git clone: {exc}")
            raise RepositoryError(f"Unexpected error while cloning repository: {str(exc)}")

    async def get_head_commit_sha(self, repo_dir: Path) -> str:
        """Extract the exact 40-character commit SHA of HEAD in a cloned repository."""
        cmd = ["git", "rev-parse", "HEAD"]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(repo_dir),
            env=self._get_hardened_env(),
        )
        stdout_bytes, stderr_bytes = await process.communicate()
        if process.returncode != 0:
            stderr_text = stderr_bytes.decode("utf-8", errors="replace").strip()
            raise RepositoryError(f"Failed to resolve Git commit SHA: {stderr_text}")

        sha = stdout_bytes.decode("utf-8").strip()
        if len(sha) != 40:
            raise RepositoryError(f"Invalid commit SHA returned: '{sha}'")
        return sha
