"""Minimal import smoke test for MCP server skeleton."""

import iridium_mcp.server as mcp_server


def test_mcp_server_imports_core_indexer() -> None:
    assert mcp_server.WorkspaceIndexer is not None
    assert callable(mcp_server.main)
