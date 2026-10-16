"""Tests for ClientScanPayload validation."""

import json
from pathlib import Path

from iridium_core import WorkspaceIndexer
from iridium_core.models.payload import ClientScanPayload


def test_payload_validate_minimal():
    payload = ClientScanPayload(
        repo_fingerprint="abc123",
        git_tree_hash="tree456",
        languages=["python"],
    )
    data = payload.model_dump()
    restored = ClientScanPayload.model_validate(data)
    assert restored.schema_version == "1"


def test_workspace_indexer_demo_target():
    # Use inline temp target instead
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    (tmp / "app.py").write_text(
        "import requests\n\ndef handler():\n    return requests.get('http://x')\n",
        encoding="utf-8",
    )
    indexer = WorkspaceIndexer(tmp, use_process_pool=False, use_cache=False)
    payload = indexer.index()
    assert payload.languages == ["python"]
    assert payload.entrypoint_count >= 0
    json.loads(payload.to_json())


def test_to_api_dict_matches_backend_shape():
    from iridium_core.models.enums import EdgeType, NodeKind
    from iridium_core.models.fragment import GraphEdge, GraphFragment, GraphNode

    payload = ClientScanPayload(
        repo_fingerprint="abc12345",
        git_tree_hash="tree45678",
        languages=["python"],
        fragments=[
            GraphFragment(
                nodes=[
                    GraphNode(
                        id="route:root",
                        kind=NodeKind.HTTP_ROUTE,
                        file="app.py",
                        line=1,
                        language="python",
                        symbol="GET /",
                    ),
                    GraphNode(
                        id="dep:requests.get",
                        kind=NodeKind.DEPENDENCY,
                        file="app.py",
                        line=2,
                        language="python",
                        symbol="requests",
                    ),
                ],
                edges=[
                    GraphEdge(
                        source="route:root", target="dep:requests.get", edge_type=EdgeType.CALLS
                    ),
                ],
            )
        ],
    )
    api = payload.to_api_dict()
    assert api["schema_version"] == "1"
    assert api["entrypoints"] == ["route:root"]
    assert len(api["nodes"]) == 2
    assert api["edges"][0]["type"] == "CALLS"
    dep_node = next(n for n in api["nodes"] if n["id"] == "dep:requests.get")
    assert dep_node["package"] == "requests"
    route_node = next(n for n in api["nodes"] if n["id"] == "route:root")
    assert route_node["label"] == "GET /"
    assert route_node["metadata"] == {"file": "app.py", "line": 1}


def test_to_api_dict_includes_determinism_warnings():
    payload = ClientScanPayload(
        repo_fingerprint="abc12345",
        git_tree_hash="tree45678",
        determinism_warnings=["DETERMINISM_WARNING: uv.lock unpinned"],
    )
    api = payload.to_api_dict()
    assert api["determinism_warnings"] == ["DETERMINISM_WARNING: uv.lock unpinned"]


def test_to_api_dict_deduplicates_edges():
    from iridium_core.models.enums import EdgeType, NodeKind
    from iridium_core.models.fragment import GraphEdge, GraphFragment, GraphNode

    edge = GraphEdge(source="a", target="b", edge_type=EdgeType.CALLS)
    payload = ClientScanPayload(
        repo_fingerprint="abc12345",
        git_tree_hash="tree45678",
        fragments=[
            GraphFragment(
                nodes=[
                    GraphNode(
                        id="a",
                        kind=NodeKind.FUNCTION,
                        file="a.py",
                        line=1,
                        language="python",
                        symbol="a",
                    ),
                    GraphNode(
                        id="b",
                        kind=NodeKind.FUNCTION,
                        file="b.py",
                        line=1,
                        language="python",
                        symbol="b",
                    ),
                ],
                edges=[edge, edge],
            )
        ],
    )
    api = payload.to_api_dict()
    assert len(api["edges"]) == 1


def test_anonymize_clears_path_bearing_warnings():
    from iridium_core.models.enums import NodeKind
    from iridium_core.models.fragment import GraphFragment, GraphNode

    payload = ClientScanPayload(
        repo_fingerprint="abc12345",
        git_tree_hash="tree45678",
        supply_chain_warnings=["read error /Users/me/secret.py: boom"],
        determinism_warnings=["DETERMINISM_WARNING: /tmp/proj/uv.lock"],
        fragments=[
            GraphFragment(
                file="secret.py",
                nodes=[
                    GraphNode(
                        id="n1",
                        kind=NodeKind.FUNCTION,
                        file="secret.py",
                        line=1,
                        language="python",
                        symbol="handler",
                    )
                ],
                warnings=["syntax error secret.py: unexpected EOF"],
            )
        ],
    )
    anon = payload.anonymize()
    assert anon.supply_chain_warnings == []
    assert anon.determinism_warnings == []
    assert anon.fragments[0].warnings == []
    assert anon.fragments[0].file.startswith("file:")
    assert anon.fragments[0].nodes[0].symbol.startswith("sym:")


def test_indexer_uv_lock_determinism_warning(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "uv.lock").write_text(
        '[[package]]\nname = "foo"\nversion = "*"\n',
        encoding="utf-8",
    )
    indexer = WorkspaceIndexer(tmp_path, use_process_pool=False, use_cache=False)
    payload = indexer.index()
    assert any("DETERMINISM_WARNING" in w for w in payload.determinism_warnings)
