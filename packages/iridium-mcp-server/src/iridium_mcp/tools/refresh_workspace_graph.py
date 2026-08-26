"""refresh_workspace_graph MCP tool."""

from __future__ import annotations

from typing import Any

from iridium_mcp.workspace import refresh_workspace_files


def run_refresh_workspace_graph(*, paths: list[str] | None = None) -> dict[str, Any]:
    payload = refresh_workspace_files(paths or [])
    return {
        "status": "ok",
        "repo_fingerprint": payload.repo_fingerprint,
        "dependency_count": payload.dependency_count,
        "entrypoint_count": payload.entrypoint_count,
        "languages": payload.languages,
        "graph_truncated": payload.graph_truncated,
    }
