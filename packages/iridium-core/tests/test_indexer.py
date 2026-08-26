"""WorkspaceIndexer integration behavior tests."""

from pathlib import Path

from iridium_core import WorkspaceIndexer


def test_empty_repo_produces_minimal_payload(tmp_path: Path) -> None:
    indexer = WorkspaceIndexer(tmp_path, use_process_pool=False, use_cache=False)
    payload = indexer.index()
    assert payload.languages == []
    assert payload.entrypoint_count == 0
    assert payload.fragments == []


def test_indexer_uses_cache_on_second_run(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("def handler():\n    pass\n", encoding="utf-8")
    first = WorkspaceIndexer(tmp_path, use_process_pool=False, use_cache=True)
    second = WorkspaceIndexer(tmp_path, use_process_pool=False, use_cache=True)
    p1 = first.index()
    p2 = second.index()
    assert p1.repo_fingerprint == p2.repo_fingerprint
    assert p1.entrypoint_count == p2.entrypoint_count


def test_indexer_detects_javascript_language(tmp_path: Path) -> None:
    (tmp_path / "index.js").write_text("export const x = 1;\n", encoding="utf-8")
    payload = WorkspaceIndexer(tmp_path, use_process_pool=False, use_cache=False).index()
    assert "javascript" in payload.languages


def test_indexer_respects_iridiumignore(tmp_path: Path) -> None:
    (tmp_path / ".iridiumignore").write_text("ignored/**\n", encoding="utf-8")
    ignored = tmp_path / "ignored"
    ignored.mkdir()
    (ignored / "secret.js").write_text("export {}\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")
    payload = WorkspaceIndexer(tmp_path, use_process_pool=False, use_cache=False).index()
    assert payload.languages == ["python"]
