""".iridiumignore glob matching."""

from __future__ import annotations

from pathlib import Path

import pathspec


def load_ignore_spec(repo: Path) -> pathspec.PathSpec | None:
    """Load .iridiumignore or return None."""
    ignore_path = repo / ".iridiumignore"
    if not ignore_path.is_file():
        return None
    try:
        lines = ignore_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    patterns = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    if not patterns:
        return None
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".iridium",
}


def should_ignore(path: Path, repo: Path, spec: pathspec.PathSpec | None) -> bool:
    """Return True if path should be excluded from indexing."""
    rel = path.relative_to(repo).as_posix()
    if any(part in DEFAULT_IGNORE_DIRS for part in path.parts):
        return True
    if spec and spec.match_file(rel):
        return True
    return False
