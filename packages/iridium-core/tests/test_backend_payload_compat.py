"""Integration: core to_api_dict() validates against backend wire schema.

Mirrors backend ``src.api.client_payloads.ClientScanPayload`` so the public
client and private API stay compatible without cross-repo imports.
"""

from typing import Literal

from iridium_core.models.enums import EdgeType, NodeKind
from iridium_core.models.fragment import GraphEdge, GraphFragment, GraphNode
from iridium_core.models.payload import ClientScanPayload as CoreClientScanPayload
from iridium_core.models.payload import DependencyNode
from pydantic import BaseModel, Field


class BackendDependencyPayload(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    version: str = Field(default="", max_length=64)
    ecosystem: Literal["pypi", "npm", "crates", "go", "maven", "other"] = "pypi"
    env_marker: str | None = None


class BackendGraphNodePayload(BaseModel):
    id: str = Field(min_length=1, max_length=256)
    type: str = Field(min_length=1, max_length=64)
    label: str | None = Field(default=None, max_length=512)
    package: str | None = Field(default=None, max_length=128)
    language: str | None = Field(default=None, max_length=32)
    metadata: dict[str, object] = Field(default_factory=dict)


class BackendGraphEdgePayload(BaseModel):
    source: str = Field(min_length=1, max_length=256)
    target: str = Field(min_length=1, max_length=256)
    type: str = Field(default="CALLS", max_length=64)
    metadata: dict[str, object] = Field(default_factory=dict)


class BackendClientScanPayload(BaseModel):
    schema_version: Literal["1"] = "1"
    repo_fingerprint: str = Field(min_length=8, max_length=256)
    git_tree_hash: str | None = Field(default=None, max_length=128)
    commit_hash: str | None = Field(default=None, max_length=128)
    client_os: str | None = Field(default=None, max_length=64)
    target_os: str | None = Field(default=None, max_length=64)
    languages: list[str] = Field(default_factory=list, max_length=32)
    dependencies: list[BackendDependencyPayload] = Field(default_factory=list, max_length=5000)
    nodes: list[BackendGraphNodePayload] = Field(default_factory=list, max_length=50000)
    edges: list[BackendGraphEdgePayload] = Field(default_factory=list, max_length=200000)
    entrypoints: list[str] = Field(default_factory=list, max_length=5000)
    supply_chain_warnings: list[str] = Field(default_factory=list, max_length=256)
    determinism_warnings: list[str] = Field(default_factory=list, max_length=256)
    graph_truncated: bool = False
    service_roots: list[str] = Field(default_factory=list, max_length=256)


def _core_sample_payload() -> CoreClientScanPayload:
    return CoreClientScanPayload(
        repo_fingerprint="blake2b:integration-test",
        git_tree_hash="tree-integration",
        languages=["python", "javascript"],
        dependencies=[
            DependencyNode(name="requests", version="2.32.0", ecosystem="pypi"),
        ],
        fragments=[
            GraphFragment(
                nodes=[
                    GraphNode(
                        id="route:get:/",
                        kind=NodeKind.HTTP_ROUTE,
                        file="app.py",
                        line=1,
                        language="python",
                        symbol="GET /",
                    ),
                    GraphNode(
                        id="dep:requests",
                        kind=NodeKind.DEPENDENCY,
                        file="app.py",
                        line=2,
                        language="python",
                        symbol="requests",
                    ),
                ],
                edges=[
                    GraphEdge(
                        source="route:get:/",
                        target="dep:requests",
                        edge_type=EdgeType.CALLS,
                    )
                ],
            )
        ],
        graph_truncated=True,
        supply_chain_warnings=["unpinned transitive dep"],
    )


def test_to_api_dict_validates_against_backend_schema() -> None:
    api_dict = _core_sample_payload().to_api_dict()
    validated = BackendClientScanPayload.model_validate(api_dict)
    assert validated.schema_version == "1"
    assert validated.repo_fingerprint.startswith("blake2b:")
    assert validated.graph_truncated is True
    assert validated.entrypoints == ["route:get:/"]
    assert any(node.package == "requests" for node in validated.nodes)
