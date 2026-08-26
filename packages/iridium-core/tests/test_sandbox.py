"""Tests for process pool batching."""

from pathlib import Path

from iridium_core.sandbox.pool import pool_worker_count, run_batched


def _echo_paths(paths: list[Path]) -> list[str]:
    return [path.name for path in paths]


def test_run_batched_empty_paths() -> None:
    results, warnings = run_batched([], _echo_paths)
    assert results == []
    assert warnings == []


def test_run_batched_processes_files(tmp_path: Path) -> None:
    files = []
    for idx in range(3):
        path = tmp_path / f"file{idx}.py"
        path.write_text("x = 1\n", encoding="utf-8")
        files.append(path)
    results, warnings = run_batched(files, _echo_paths, max_workers=1)
    assert sorted(results) == ["file0.py", "file1.py", "file2.py"]
    assert warnings == []


def test_pool_worker_count_is_positive() -> None:
    assert pool_worker_count() >= 1
