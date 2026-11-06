"""Base service class for domain business logic."""

from abc import ABC
from app.core.logging import get_logger


class BaseService(ABC):
    """Abstract base class providing logging and shared lifecycle helpers."""

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
