"""Language extractor plugin interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iridium_core.models.fragment import GraphFragment


class ImportMap(dict[str, str]):
    """Maps import specifier → resolved file path."""


class LanguageExtractor(ABC):
    language: str

    @abstractmethod
    def parse_batch_safe(self, paths: list[Path]) -> list[GraphFragment]:
        """Parse a batch of source files into graph fragments."""

    @abstractmethod
    def resolve_imports(self, repo: Path) -> ImportMap:
        """Build import resolution map for the repository."""

    def supported_extensions(self) -> set[str]:
        return set()
