"""Import smoke tests for MCP server."""

import iridium_mcp.server as mcp_server
from iridium_core import WorkspaceIndexer


def test_mcp_server_exports_tools() -> None:
    assert callable(mcp_server.main)
    assert callable(mcp_server.validate_dependency_addition)
    assert WorkspaceIndexer is not None
