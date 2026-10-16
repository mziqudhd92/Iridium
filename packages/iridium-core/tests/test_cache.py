"""Tests for AST cache."""

from pathlib import Path

from iridium_core.cache.ast_cache import AstCache, content_hash, resolve_cache_path
from iridium_core.models.fragment import GraphFragment


def test_content_hash_stable():
    data = b"print('hello')"
    assert content_hash(data) == content_hash(data)
    assert content_hash(data) != content_hash(b"other")


def test_ast_cache_roundtrip(tmp_path: Path):
    db_path = tmp_path / "cache.db"
    fragment = GraphFragment(nodes=[], edges=[], warnings=["ok"])
    with AstCache(db_path) as cache:
        cache.put("tree1", "app.py", "hash1", fragment.model_dump_json(), "commit1")
        loaded = cache.get("tree1", "app.py", "hash1")
    assert loaded is not None
    restored = GraphFragment.model_validate_json(loaded)
    assert restored.warnings == ["ok"]


def test_resolve_cache_path_local(tmp_path: Path):
    path = resolve_cache_path(tmp_path)
    assert path == tmp_path / ".iridium" / "cache.db"


def test_wal_pragmas_applied(tmp_path: Path):
    db_path = tmp_path / "cache.db"
    with AstCache(db_path) as cache:
        mode = cache._conn.execute("PRAGMA journal_mode").fetchone()[0]
    assert mode.lower() == "wal"


def test_ast_cache_falls_back_across_tree_hashes(tmp_path: Path) -> None:
    db_path = tmp_path / "cache.db"
    fragment = GraphFragment(file="app.py", warnings=["cached"])
    with AstCache(db_path) as cache:
        cache.put("tree-old", "app.py", "hash-same", fragment.model_dump_json(), "c1")
        loaded = cache.get("tree-new", "app.py", "hash-same")
    assert loaded is not None
    assert GraphFragment.model_validate_json(loaded).warnings == ["cached"]


def test_ast_cache_prune_removes_stale_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "cache.db"
    fragment = GraphFragment(file="app.py")
    with AstCache(db_path) as cache:
        cache.put("tree1", "app.py", "h1", fragment.model_dump_json(), "c1")
        cache._conn.execute("UPDATE ast_cache SET updated_at = datetime('now', '-60 days')")
        cache._conn.commit()
        removed = cache.prune(max_age_days=30)
        assert removed == 1
        assert cache.get("tree1", "app.py", "h1") is None
