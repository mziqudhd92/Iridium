"""Git helpers for cache keys and shallow clone detection."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def _run_git(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None


def git_tree_hash(repo: Path) -> str:
    """Return git tree hash for HEAD, or synthetic hash for non-git dirs."""
    tree = _run_git(repo, "rev-parse", "HEAD^{tree}")
    if tree:
        return tree
    # Fallback: hash all file paths + mtimes for non-git workspaces
    digest = hashlib.sha256()
    for path in sorted(repo.rglob("*")):
        if path.is_file() and ".git" not in path.parts:
            rel = path.relative_to(repo).as_posix()
            digest.update(rel.encode())
            try:
                digest.update(str(path.stat().st_mtime_ns).encode())
            except OSError:
                pass
    return f"nogit:{digest.hexdigest()[:40]}"


def git_commit_hash(repo: Path) -> str | None:
    return _run_git(repo, "rev-parse", "HEAD")


def is_shallow_repository(repo: Path) -> bool:
    value = _run_git(repo, "rev-parse", "--is-shallow-repository")
    return value == "true"


def repo_fingerprint(repo: Path) -> str:
    """Stable fingerprint for repo identity (path + remote url)."""
    remote = _run_git(repo, "remote", "get-url", "origin") or str(repo.resolve())
    return hashlib.sha256(remote.encode()).hexdigest()[:32]
