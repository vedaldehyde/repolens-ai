"""Schemas for natural-language codebase queries."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """File and line reference supporting an answer."""

    file_path: str = Field(..., description="Repository relative file path")
    start_line: int = Field(..., description="Starting line number")
    end_line: int = Field(..., description="Ending line number")
    snippet: Optional[str] = Field(default=None, description="Relevant code snippet")


class QueryRequest(BaseModel):
    """Payload for asking questions about an ingested codebase."""

    repository_id: str = Field(..., description="Target repository ID")
    question: str = Field(..., min_length=3, max_length=1000, description="User's query")


class QueryResponse(BaseModel):
    """AI agentic answer response."""

    answer: str = Field(..., description="Synthesized answer from LangGraph agent")
    citations: List[Citation] = Field(default_factory=list, description="Referenced code files and symbols")
    execution_steps: List[str] = Field(
        default_factory=list,
        description="Reasoning traces or tool execution steps taken",
    )
