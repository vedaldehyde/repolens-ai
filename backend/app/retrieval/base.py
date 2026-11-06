"""Retrieval and vector storage interfaces.

Scaffolding for Phase 3+: SentenceTransformers embeddings and ChromaDB vector store.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SearchResult:
    """Retrieved code chunk or symbol with similarity score."""

    document_id: str
    content: str
    metadata: Dict[str, Any]
    score: float


class BaseVectorStore(ABC):
    """Abstract interface for vector database operations."""

    @abstractmethod
    async def index_chunks(self, repository_id: str, chunks: List[Dict[str, Any]]) -> int:
        """Store chunked code representations and embeddings into the collection.

        Implementation deferred to Phase 3.
        """
        pass

    @abstractmethod
    async def similarity_search(
        self,
        repository_id: str,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Perform semantic retrieval against indexed codebase collections.

        Implementation deferred to Phase 3.
        """
        pass
