"""get_reachability_context MCP tool."""

from __future__ import annotations

from typing import Any

from iridium_mcp.api_client import QueryApiClient
from iridium_mcp.workspace import get_warm_payload, warm_index_workspace


def run_get_reachability_context(
    *,
    package: str,
    symbol: str,
    cve_id: str | None = None,
    target_file: str | None = None,
    api_client: QueryApiClient | None = None,
) -> dict[str, Any]:
    payload = get_warm_payload() or warm_index_workspace(use_process_pool=False)
    api = api_client or QueryApiClient()
    query = {
        "package": package,
        "symbol": symbol,
        "cve_id": cve_id,
        "target_file": target_file,
        "repo_fingerprint": payload.repo_fingerprint,
        "graph": payload.to_api_dict(),
    }
    return api.reachability_context(query)
