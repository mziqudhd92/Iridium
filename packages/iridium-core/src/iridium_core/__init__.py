"""Iridium core — local extraction, graph assembly, and caching."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def resolve_package_version(
    dist_name: str = "iridium-core",
    anchor_file: str | Path | None = None,
) -> str:
    """Resolve installed package version with fallback to repo VERSION file."""
    try:
        return version(dist_name)
    except PackageNotFoundError:  # pragma: no cover - source-tree / unset install
        anchor = Path(anchor_file or __file__).resolve()
        for parent in anchor.parents:
            candidate = parent / "VERSION"
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8").strip()
        return "0.0.0"


def _resolve_version() -> str:
    return resolve_package_version("iridium-core", __file__)


__version__ = _resolve_version()

from iridium_core.workspace.indexer import WorkspaceIndexer

__all__ = ["WorkspaceIndexer", "__version__", "resolve_package_version"]
