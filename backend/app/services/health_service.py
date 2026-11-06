"""Health service providing application operational metrics."""

import time
from app.core.config import Settings, get_settings
from app.schemas.common import HealthStatusResponse
from app.services.base import BaseService

START_TIME = time.time()


class HealthService(BaseService):
    """Service to evaluate backend health and runtime diagnostics."""

    def __init__(self, settings: Settings = get_settings()) -> None:
        super().__init__()
        self.settings = settings

    def check_health(self) -> HealthStatusResponse:
        """Perform system diagnostics and return health status."""
        uptime = round(time.time() - START_TIME, 2)

        # Basic storage diagnostics
        repos_dir = self.settings.absolute_repos_dir
        chroma_dir = self.settings.absolute_chroma_dir

        details = {
            "storage": {
                "repos_dir_exists": repos_dir.exists(),
                "chroma_dir_exists": chroma_dir.exists(),
            },
            "environment": self.settings.ENVIRONMENT,
            "debug": self.settings.DEBUG,
        }

        return HealthStatusResponse(
            status="healthy",
            version=self.settings.VERSION,
            environment=self.settings.ENVIRONMENT,
            uptime_seconds=uptime,
            details=details,
        )
