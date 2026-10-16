"""Workspace lifecycle helpers for MCP server."""

from __future__ import annotations

import os
import threading
from pathlib import Path

from iridium_core import WorkspaceIndexer
from iridium_core.models.enums import NodeKind
from iridium_core.models.fragment import GraphFragment
from iridium_core.models.payload import ClientScanPayload

_audit_lock = threading.Lock()
_index_lock = threading.Lock()
_index_exec_lock = threading.Lock()
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


def _merge_payloads(
    base: ClientScanPayload,
    delta: ClientScanPayload,
    *,
    refreshed_files: set[str] | None = None,
) -> ClientScanPayload:
    evict_files = refreshed_files or {
        node.file for frag in delta.fragments for node in frag.nodes if node.file
    }
    evicted_node_ids: set[str] = set()
    retained_base_fragments: list[GraphFragment] = []

    for fragment in base.fragments:
        kept_nodes = []
        for node in fragment.nodes:
            # Dependency nodes are workspace-global (shared across files).
            if node.kind == NodeKind.DEPENDENCY:
                kept_nodes.append(node)
                continue
            if node.file and node.file in evict_files:
                evicted_node_ids.add(node.id)
            else:
                kept_nodes.append(node)
        kept_edges = [
            edge
            for edge in fragment.edges
            if edge.source not in evicted_node_ids and edge.target not in evicted_node_ids
        ]
        retained_base_fragments.append(
            GraphFragment(
                file=fragment.file,
                nodes=kept_nodes,
                edges=kept_edges,
                warnings=list(fragment.warnings),
            )
        )

    merged_fragment = GraphFragment()
    for fragment in retained_base_fragments:
        merged_fragment = merged_fragment.merge(fragment)
    for fragment in delta.fragments:
        merged_fragment = merged_fragment.merge(fragment)

    entrypoints = sum(
        1
        for n in merged_fragment.nodes
        if n.kind in (NodeKind.HTTP_ROUTE, NodeKind.DYNAMIC_ENTRYPOINT)
    )
    deps = delta.dependencies or base.dependencies
    langs = sorted(set(base.languages) | set(delta.languages))

    return base.model_copy(
        update={
            "languages": langs,
            "fragments": [merged_fragment] if merged_fragment.nodes else [],
            "dependencies": deps,
            "graph_truncated": base.graph_truncated or delta.graph_truncated,
            "supply_chain_warnings": list(
                dict.fromkeys(base.supply_chain_warnings + delta.supply_chain_warnings)
            ),
            "determinism_warnings": list(
                dict.fromkeys(base.determinism_warnings + delta.determinism_warnings)
            ),
            "entrypoint_count": entrypoints,
            "dependency_count": len(deps),
        }
    )


def warm_index_workspace(
    *, root: Path | None = None, use_process_pool: bool = False
) -> ClientScanPayload:
    global _indexing
    target = (root or workspace_root()).resolve()
    with _index_exec_lock:
        with _index_lock:
            _indexing = True
        try:
            indexer = WorkspaceIndexer(target, use_process_pool=use_process_pool)
            payload = indexer.index()
            return _set_warm_payload(payload)
        finally:
            with _index_lock:
                _indexing = False


def refresh_workspace_files(paths: list[str], *, root: Path | None = None) -> ClientScanPayload:
    """Re-parse changed files and merge into the warm graph."""
    target = (root or workspace_root()).resolve()
    append_audit(f"refresh_workspace_graph paths={len(paths)}", root=target)
    if not paths:
        return warm_index_workspace(root=target, use_process_pool=False)

    resolved: list[Path] = []
    refreshed_rels: set[str] = set()
    for raw in paths:
        candidate = (target / raw).resolve()
        if not candidate.is_relative_to(target):
            continue
        rel = candidate.relative_to(target).as_posix()
        refreshed_rels.add(rel)
        if candidate.is_file():
            resolved.append(candidate)

    if not refreshed_rels:
        return warm_index_workspace(root=target, use_process_pool=False)

    with _index_exec_lock:
        existing = get_warm_payload()
        if not resolved:
            if existing is None:
                # Fall through to full reindex outside this lock.
                pass
            else:
                empty_delta = existing.model_copy(update={"fragments": []})
                return _set_warm_payload(
                    _merge_payloads(existing, empty_delta, refreshed_files=refreshed_rels)
                )
        else:
            indexer = WorkspaceIndexer(target, use_process_pool=False, only_paths=resolved)
            delta = indexer.index()
            if existing is None:
                return _set_warm_payload(delta)
            return _set_warm_payload(
                _merge_payloads(existing, delta, refreshed_files=refreshed_rels)
            )

    return warm_index_workspace(root=target, use_process_pool=False)
