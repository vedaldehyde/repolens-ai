"""AI agent orchestration interfaces.

Scaffolding for Phase 4: LangGraph multi-step reasoning, retrieval augmentation,
and Groq LLM synthesis.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional
from app.schemas.query import QueryResponse


class BaseCodebaseAgent(ABC):
    """Abstract interface for LangGraph codebase exploration agents."""

    @abstractmethod
    async def ask(
        self,
        repository_id: str,
        question: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> QueryResponse:
        """Process user question through multi-step agent reasoning workflow.

        Implementation deferred to Phase 4.
        """
        pass

    @abstractmethod
    async def stream_ask(
        self,
        repository_id: str,
        question: str,
    ) -> AsyncGenerator[str, None]:
        """Stream tokenized reasoning or responses.

        Implementation deferred to Phase 4.
        """
        pass
