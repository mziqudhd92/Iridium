"""Client scan payload schema (local serialization, no network I/O)."""

from __future__ import annotations

import json
import platform
from typing import Any

from pydantic import BaseModel, Field

from iridium_core.models.enums import NodeKind
from iridium_core.models.fragment import GraphFragment


class DependencyNode(BaseModel):
    name: str
    version: str | None = None
    ecosystem: str = "pypi"
    resolved_url: str | None = None
    env_marker: str | None = None


class ClientScanPayload(BaseModel):
    schema_version: str = "1"
    repo_fingerprint: str
    git_tree_hash: str
    commit_hash: str | None = None
    client_os: str = Field(default_factory=lambda: platform.system().lower())
    languages: list[str] = Field(default_factory=list)
    fragments: list[GraphFragment] = Field(default_factory=list)
    dependencies: list[DependencyNode] = Field(default_factory=list)
    graph_truncated: bool = False
    supply_chain_warnings: list[str] = Field(default_factory=list)
    determinism_warnings: list[str] = Field(default_factory=list)
    entrypoint_count: int = 0
    dependency_count: int = 0

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(mode="json"), indent=indent)

    def to_msgpack(self) -> bytes:
        try:
            import msgpack
        except ImportError as exc:
            raise RuntimeError("msgpack extra required: pip install iridium-core[msgpack]") from exc
        return msgpack.packb(self.model_dump(mode="json"), use_bin_type=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClientScanPayload:
        return cls.model_validate(data)

    def to_api_dict(self) -> dict[str, Any]:
        """Flatten fragments into backend /api/v1/client/scan wire format."""
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        entrypoints: list[str] = []
        seen_node_ids: set[str] = set()

        for fragment in self.fragments:
            for node in fragment.nodes:
                if node.id in seen_node_ids:
                    continue
                seen_node_ids.add(node.id)
                api_node: dict[str, Any] = {
                    "id": node.id,
                    "type": node.kind.value,
                    "language": node.language or None,
                    "metadata": {"file": node.file, "line": node.line},
                }
                if node.symbol:
                    api_node["label"] = node.symbol
                if node.kind == NodeKind.DEPENDENCY:
                    api_node["package"] = node.symbol or None
                nodes.append(api_node)
                if node.kind in (NodeKind.HTTP_ROUTE, NodeKind.DYNAMIC_ENTRYPOINT):
                    entrypoints.append(node.id)

            for edge in fragment.edges:
                edges.append(
                    {
                        "source": edge.source,
                        "target": edge.target,
                        "type": edge.edge_type.value,
                    }
                )

        return {
            "schema_version": self.schema_version,
            "repo_fingerprint": self.repo_fingerprint,
            "git_tree_hash": self.git_tree_hash,
            "commit_hash": self.commit_hash,
            "client_os": self.client_os,
            "languages": self.languages,
            "dependencies": [
                {
                    "name": dep.name,
                    "version": dep.version or "",
                    "ecosystem": dep.ecosystem,
                    "env_marker": dep.env_marker,
                }
                for dep in self.dependencies
            ],
            "nodes": nodes,
            "edges": edges,
            "entrypoints": entrypoints,
            "graph_truncated": self.graph_truncated,
            "supply_chain_warnings": self.supply_chain_warnings,
        }
