"""Tests for MCP tool implementations."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from iridium_mcp.api_client import QueryApiClient
from iridium_mcp.tools.reachability_context import run_get_reachability_context
from iridium_mcp.tools.refresh_workspace_graph import run_refresh_workspace_graph
from iridium_mcp.tools.validate_dependency import run_validate_dependency_addition
from iridium_mcp.workspace import get_warm_payload, refresh_workspace_files, warm_index_workspace


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


def test_refresh_workspace_files_evicts_stale_nodes_and_rejects_outside_paths(
    tmp_path: Path,
) -> None:
    app_file = tmp_path / "app.py"
    app_file.write_text(
        "@app.get('/v1')\ndef old_handler():\n    return 1\n",
        encoding="utf-8",
    )
    warm_index_workspace(root=tmp_path, use_process_pool=False)
    initial = get_warm_payload()
    assert initial is not None
    assert any(n.symbol == "old_handler" for n in initial.fragments[0].nodes)

    app_file.write_text(
        "@app.get('/v2')\ndef new_handler():\n    return 2\n",
        encoding="utf-8",
    )
    updated = refresh_workspace_files(["app.py", "../outside.py"], root=tmp_path)
    symbols = {n.symbol for n in updated.fragments[0].nodes}
    assert "new_handler" in symbols
    assert "old_handler" not in symbols
    assert updated.entrypoint_count == 1
    status = run_refresh_workspace_graph(paths=["app.py"])
    assert status["status"] == "ok"


def test_refresh_preserves_shared_dependency_edges_from_other_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "uv.lock").write_text(
        'version = 1\n[[package]]\nname = "requests"\nversion = "2.32.3"\n',
        encoding="utf-8",
    )
    (tmp_path / "a.py").write_text(
        "import requests\ndef fa():\n    return requests.get('x')\n",
        encoding="utf-8",
    )
    (tmp_path / "b.py").write_text(
        "import requests\ndef fb():\n    return requests.get('y')\n",
        encoding="utf-8",
    )
    warm_index_workspace(root=tmp_path, use_process_pool=False)
    before = get_warm_payload()
    assert before is not None
    b_nodes = {n.id for n in before.fragments[0].nodes if n.file == "b.py"}
    before_b_dep_edges = [
        e for e in before.fragments[0].edges if e.source in b_nodes and e.target == "dep:requests"
    ]
    assert before_b_dep_edges

    (tmp_path / "a.py").write_text(
        "import requests\ndef fa2():\n    return requests.get('x')\n",
        encoding="utf-8",
    )
    after = refresh_workspace_files(["a.py"], root=tmp_path)
    b_nodes = {n.id for n in after.fragments[0].nodes if n.file == "b.py"}
    after_b_dep_edges = [
        e for e in after.fragments[0].edges if e.source in b_nodes and e.target == "dep:requests"
    ]
    assert after_b_dep_edges
    assert any(n.id == "dep:requests" for n in after.fragments[0].nodes)
