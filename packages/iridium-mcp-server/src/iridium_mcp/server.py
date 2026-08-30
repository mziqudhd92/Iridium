"""MCP server — stdio transport with runtime guardrail tools (Phase 2)."""

from __future__ import annotations

import os
import threading
import time

from mcp.server.mcpserver import MCPServer

from iridium_mcp.indexer import start_background_index
from iridium_mcp.tools.reachability_context import run_get_reachability_context
from iridium_mcp.tools.refresh_workspace_graph import run_refresh_workspace_graph
from iridium_mcp.tools.validate_dependency import run_validate_dependency_addition
from iridium_mcp.workspace import append_audit, workspace_root

mcp = MCPServer("iridium-mcp-server", version="0.5.0")


def _start_parent_heartbeat() -> threading.Thread:
    def _run() -> None:
        while True:
            time.sleep(2.0)
            if os.getppid() == 1:
                append_audit("parent process exited; shutting down MCP server")
                os._exit(0)

    thread = threading.Thread(target=_run, name="iridium-parent-heartbeat", daemon=True)
    thread.start()
    return thread


@mcp.tool(
    name="validate_dependency_addition",
    description=(
        "Checks if importing a specific package version creates a reachable vulnerability "
        "in the current AST graph. Call BEFORE adding any import or dependency."
    ),
)
def validate_dependency_addition(
    package: str,
    version: str,
    target_file: str,
    ecosystem: str = "pypi",
) -> dict:
    return run_validate_dependency_addition(
        package=package,
        version=version,
        target_file=target_file,
        ecosystem=ecosystem,
    )


@mcp.tool(
    name="get_reachability_context",
    description=(
        "Returns the execution path from HTTP/API entrypoints to a vulnerable function, "
        "formatted for agent context. Use after validate_dependency_addition "
        "returns reachable=true."
    ),
)
def get_reachability_context(
    package: str,
    symbol: str,
    cve_id: str | None = None,
    target_file: str | None = None,
) -> dict:
    return run_get_reachability_context(
        package=package,
        symbol=symbol,
        cve_id=cve_id,
        target_file=target_file,
    )


@mcp.tool(
    name="refresh_workspace_graph",
    description="Lightweight delta re-parse when agent saves files. Keeps warm graph current.",
)
def refresh_workspace_graph(paths: list[str] | None = None) -> dict:
    return run_refresh_workspace_graph(paths=paths)


def main() -> None:
    root = workspace_root()
    append_audit(f"iridium-mcp-server starting workspace={root}")
    _start_parent_heartbeat()
    start_background_index(root=root)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
