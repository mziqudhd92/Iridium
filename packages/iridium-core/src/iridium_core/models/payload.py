"""Client scan payload schema (local serialization, no network I/O)."""

from __future__ import annotations

import json
import platform
from typing import Any

from pydantic import BaseModel, Field

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
