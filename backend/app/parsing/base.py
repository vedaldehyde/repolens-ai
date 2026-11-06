"""Code parsing interfaces and data structures.

Scaffolding for Phase 2+: Python AST and multi-language Tree-sitter parsers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CodeSymbol:
    """Represents an extracted code symbol (function, class, method)."""

    name: str
    kind: str  # function, class, method, variable
    file_path: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)


@dataclass
class ParsedFile:
    """Represents a parsed source file and its symbols."""

    file_path: str
    language: str
    symbols: List[CodeSymbol] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


class BaseCodeParser(ABC):
    """Abstract interface for language-specific code parsers."""

    @abstractmethod
    def parse_file(self, file_path: Path) -> ParsedFile:
        """Parse an individual source code file into structured symbols.

        Implementation deferred to Phase 2.
        """
        pass

    @abstractmethod
    def parse_directory(self, root_dir: Path) -> List[ParsedFile]:
        """Recursively scan and parse all supported files in a directory.

        Implementation deferred to Phase 2.
        """
        pass
