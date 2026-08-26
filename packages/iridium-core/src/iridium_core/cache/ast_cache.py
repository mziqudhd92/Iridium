"""SQLite AST cache with WAL and cross-mount fallback."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Self

WAL_PRAGMAS = (
    "PRAGMA journal_mode=WAL",
    "PRAGMA busy_timeout=5000",
    "PRAGMA mmap_size=268435456",
)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS ast_cache (
    git_tree_hash TEXT NOT NULL,
    file_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    commit_hash TEXT,
    fragment_json TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (git_tree_hash, file_path, content_hash)
)
"""


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_cross_mount(path: Path) -> bool:
    """Heuristic: repo on /mnt/ (WSL) or common Docker bind mounts."""
    posix = path.as_posix()
    if posix.startswith("/mnt/"):
        return True
    home = Path.home().as_posix()
    if not posix.startswith(home) and posix.startswith("/Users/"):
        return False
    # On Linux docker bind mounts often under /workspace or /repo
    for prefix in ("/workspace", "/repo", "/host_mnt"):
        if posix.startswith(prefix):
            return True
    return False


def resolve_cache_path(repo: Path) -> Path:
    """Return active cache.db path; fallback to ~/.cache/iridium on cross-mount."""
    local = repo / ".iridium" / "cache.db"
    if not _is_cross_mount(repo.resolve()):
        local.parent.mkdir(parents=True, exist_ok=True)
        return local

    repo_hash = hashlib.sha256(str(repo.resolve()).encode()).hexdigest()[:16]
    fallback = Path.home() / ".cache" / "iridium" / f"{repo_hash}" / "cache.db"
    fallback.parent.mkdir(parents=True, exist_ok=True)
    return fallback


class AstCache:
    """WAL-backed AST fragment cache keyed by git tree hash."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), timeout=5.0)
        for pragma in WAL_PRAGMAS:
            self._conn.execute(pragma)
        self._conn.execute(CREATE_TABLE)
        self._conn.commit()

    def get(
        self,
        git_tree_hash: str,
        file_path: str,
        file_content_hash: str,
    ) -> str | None:
        row = self._conn.execute(
            "SELECT fragment_json FROM ast_cache "
            "WHERE git_tree_hash=? AND file_path=? AND content_hash=?",
            (git_tree_hash, file_path, file_content_hash),
        ).fetchone()
        return row[0] if row else None

    def put(
        self,
        git_tree_hash: str,
        file_path: str,
        file_content_hash: str,
        fragment_json: str,
        commit_hash: str | None = None,
    ) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO ast_cache "
            "(git_tree_hash, file_path, content_hash, commit_hash, fragment_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (git_tree_hash, file_path, file_content_hash, commit_hash, fragment_json),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
