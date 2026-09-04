"""Iridium core — local extraction, graph assembly, and caching."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _resolve_version() -> str:
    try:
        return version("iridium-core")
    except PackageNotFoundError:  # pragma: no cover - source-tree / unset install
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "VERSION"
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8").strip()
        return "0.0.0"


__version__ = _resolve_version()

from iridium_core.workspace.indexer import WorkspaceIndexer  # noqa: E402

__all__ = ["WorkspaceIndexer"]
