"""Tests for git fingerprint helpers."""

from pathlib import Path

from iridium_core.git.tree_hash import git_commit_hash, git_tree_hash, repo_fingerprint


def test_nogit_tree_hash_is_stable_for_same_content(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    first = git_tree_hash(tmp_path)
    second = git_tree_hash(tmp_path)
    assert first.startswith("nogit:")
    assert first == second


def test_repo_fingerprint_uses_path_when_not_git(tmp_path: Path) -> None:
    fp = repo_fingerprint(tmp_path)
    assert fp.startswith("blake2b:")
    assert len(fp) > len("blake2b:")
    assert git_commit_hash(tmp_path) is None
