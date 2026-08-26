"""Tests for MCP tool implementations."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from iridium_mcp.api_client import QueryApiClient
from iridium_mcp.tools.reachability_context import run_get_reachability_context
from iridium_mcp.tools.validate_dependency import run_validate_dependency_addition
from iridium_mcp.workspace import warm_index_workspace


def test_validate_dependency_fail_open_on_api_error(tmp_path: Path) -> None:
    warm_index_workspace(root=tmp_path, use_process_pool=False)
    api = QueryApiClient(api_url="https://invalid.example.com", timeout=0.01)
    result = run_validate_dependency_addition(
        package="requests",
        version="2.25.0",
        target_file="app.py",
        api_client=api,
    )
    assert result["allowed"] is True
    assert result["degraded"] is True


def test_validate_dependency_blocks_when_api_denies(tmp_path: Path) -> None:
    warm_index_workspace(root=tmp_path, use_process_pool=False)
    api = MagicMock(spec=QueryApiClient)
    api.validate_dependency.return_value = {
        "allowed": False,
        "risk_score": 0.9,
        "cves": [{"id": "CVE-TEST", "severity": "HIGH", "reachable": True}],
        "recommendation": "upgrade",
        "safe_alternatives": [],
    }
    result = run_validate_dependency_addition(
        package="flask",
        version="2.0.0",
        target_file="app.py",
        api_client=api,
    )
    assert result["allowed"] is False
    assert result["risk_score"] == 0.9


def test_reachability_context_returns_rewrite_hints(tmp_path: Path) -> None:
    warm_index_workspace(root=tmp_path, use_process_pool=False)
    api = MagicMock(spec=QueryApiClient)
    api.reachability_context.return_value = {
        "entrypoints": ["GET /"],
        "call_path_compressed": ["route → handler"],
        "call_path_full": ["route → handler → sink"],
        "rewrite_hints": ["pin requests>=2.32.0"],
        "secure_interface_stub": "def get(...): ...",
        "secure_interface_docstring": "safe GET",
        "patch_available": True,
        "patch_registry_hit": True,
        "degraded": False,
    }
    result = run_get_reachability_context(package="requests", symbol="requests.get", api_client=api)
    assert result["rewrite_hints"]
    assert result["secure_interface_stub"]
