"""Workspace lifecycle helpers for MCP server."""

from __future__ import annotations

import os
import threading
from pathlib import Path

from iridium_core import WorkspaceIndexer
from iridium_core.models.fragment import GraphFragment
from iridium_core.models.payload import ClientScanPayload

_audit_lock = threading.Lock()
_index_lock = threading.Lock()
_warm_payload: ClientScanPayload | None = None
_indexing = False


def workspace_root() -> Path:
    return Path(os.environ.get("IRIDIUM_WORKSPACE", os.getcwd())).resolve()


def iridium_dir(root: Path | None = None) -> Path:
    target = (root or workspace_root()) / ".iridium"
    target.mkdir(parents=True, exist_ok=True)
    return target


def audit_log_path(root: Path | None = None) -> Path:
    return iridium_dir(root) / "audit.log"


def append_audit(message: str, *, root: Path | None = None) -> None:
    path = audit_log_path(root)
    line = message.strip()
    if not line:
        return
    with _audit_lock, path.open("a", encoding="utf-8") as handle:
        handle.write(f"{line}\n")


def get_warm_payload() -> ClientScanPayload | None:
    with _index_lock:
        return _warm_payload


def is_indexing() -> bool:
    with _index_lock:
        return _indexing


def _set_warm_payload(payload: ClientScanPayload) -> ClientScanPayload:
    global _warm_payload
    with _index_lock:
        _warm_payload = payload
    return payload


def _merge_payloads(base: ClientScanPayload, delta: ClientScanPayload) -> ClientScanPayload:
    merged_fragment = GraphFragment()
    for fragment in base.fragments:
        merged_fragment = merged_fragment.merge(fragment)
    for fragment in delta.fragments:
        merged_fragment = merged_fragment.merge(fragment)
    return base.model_copy(
        update={
            "fragments": [merged_fragment] if merged_fragment.nodes else base.fragments,
            "dependencies": delta.dependencies or base.dependencies,
            "graph_truncated": base.graph_truncated or delta.graph_truncated,
            "supply_chain_warnings": list(
                dict.fromkeys(base.supply_chain_warnings + delta.supply_chain_warnings)
            ),
            "determinism_warnings": list(
                dict.fromkeys(base.determinism_warnings + delta.determinism_warnings)
            ),
            "entrypoint_count": max(base.entrypoint_count, delta.entrypoint_count),
            "dependency_count": max(base.dependency_count, delta.dependency_count),
        }
    )


def warm_index_workspace(
    *, root: Path | None = None, use_process_pool: bool = False
) -> ClientScanPayload:
    global _indexing
    target = root or workspace_root()
    with _index_lock:
        _indexing = True
    try:
        indexer = WorkspaceIndexer(target, use_process_pool=use_process_pool)
        payload = indexer.index()
        with _index_lock:
            _indexing = False
        return _set_warm_payload(payload)
    except Exception:
        with _index_lock:
            _indexing = False
        raise


def refresh_workspace_files(paths: list[str], *, root: Path | None = None) -> ClientScanPayload:
    """Re-parse changed files and merge into the warm graph."""
    target = root or workspace_root()
    append_audit(f"refresh_workspace_graph paths={len(paths)}", root=root)
    if not paths:
        return warm_index_workspace(root=root, use_process_pool=False)
    resolved = []
    for raw in paths:
        candidate = (target / raw).resolve()
        if candidate.is_file():
            resolved.append(candidate)
    if not resolved:
        return warm_index_workspace(root=root, use_process_pool=False)
    indexer = WorkspaceIndexer(target, use_process_pool=False, only_paths=resolved)
    delta = indexer.index()
    existing = get_warm_payload()
    if existing is None:
        return _set_warm_payload(delta)
    return _set_warm_payload(_merge_payloads(existing, delta))
