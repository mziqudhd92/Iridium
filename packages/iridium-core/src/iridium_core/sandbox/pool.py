"""Process pool for batched file parsing."""

from __future__ import annotations

import os
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import TypeVar

BATCH_SIZE = 50
BATCH_TIMEOUT_SECONDS = 10

T = TypeVar("T")


def cgroup_memory_limit_mb() -> int | None:
    """Read cgroup v2 memory.max; return limit in MB or None."""
    for path in (
        Path("/sys/fs/cgroup/memory.max"),
        Path("/sys/fs/cgroup/memory/memory.limit_in_bytes"),
    ):
        if not path.is_file():
            continue
        try:
            raw = path.read_text().strip()
            if raw == "max":
                return None
            bytes_limit = int(raw)
            return max(1, bytes_limit // (1024 * 1024))
        except (OSError, ValueError):
            continue
    return None


def pool_worker_count() -> int:
    """Size pool as min(cpu_count, cgroup_ram_mb // 128)."""
    cpu = os.cpu_count() or 1
    ram_mb = cgroup_memory_limit_mb()
    if ram_mb is None:
        return cpu
    cgroup_cap = max(1, ram_mb // 128)
    return max(1, min(cpu, cgroup_cap))


def _chunked(items: list[Path], size: int) -> list[list[Path]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def run_batched(
    paths: list[Path],
    worker_fn: Callable[[list[Path]], list[T]],
    *,
    batch_size: int = BATCH_SIZE,
    timeout: float = BATCH_TIMEOUT_SECONDS,
    max_workers: int | None = None,
) -> tuple[list[T], list[str]]:
    """Execute worker_fn on path batches via ProcessPoolExecutor."""
    if not paths:
        return [], []

    workers = max_workers or pool_worker_count()
    results: list[T] = []
    warnings: list[str] = []
    batches = _chunked(paths, batch_size)

    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(worker_fn, batch) for batch in batches]
        for idx, future in enumerate(futures):
            try:
                batch_result = future.result(timeout=timeout)
                results.extend(batch_result)
            except FuturesTimeoutError:
                warnings.append(f"batch {idx} timed out after {timeout}s")
            except Exception as exc:  # noqa: BLE001 — continue on worker crash
                warnings.append(f"batch {idx} failed: {exc}")

    return results, warnings
