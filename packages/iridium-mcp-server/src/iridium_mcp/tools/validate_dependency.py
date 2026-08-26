"""validate_dependency_addition MCP tool."""

from __future__ import annotations

from typing import Any

from iridium_mcp.api_client import QueryApiClient
from iridium_mcp.workspace import append_audit, get_warm_payload, is_indexing, warm_index_workspace


def run_validate_dependency_addition(
    *,
    package: str,
    version: str,
    target_file: str,
    ecosystem: str = "pypi",
    api_client: QueryApiClient | None = None,
) -> dict[str, Any]:
    payload = get_warm_payload()
    if payload is None:
        if is_indexing():
            return {
                "allowed": True,
                "indexing": True,
                "warning": "Workspace graph warming; dependency-only check deferred.",
                "degraded": True,
            }
        payload = warm_index_workspace(use_process_pool=False)
    api = api_client or QueryApiClient()
    query = {
        "package": package,
        "version": version,
        "target_file": target_file,
        "ecosystem": ecosystem,
        "repo_fingerprint": payload.repo_fingerprint if payload else "blake2b:cold",
        "graph": payload.to_api_dict() if payload else None,
    }
    result = api.validate_dependency(query)
    if not result.get("allowed", True):
        append_audit(f"blocked dependency {package}=={version} for {target_file}")
    return result
