"""Graph fragment node and edge models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from iridium_core.models.enums import EdgeType, NodeKind


class GraphNode(BaseModel):
    id: str
    kind: NodeKind
    file: str
    line: int = 0
    language: str = ""
    symbol: str = ""


class GraphEdge(BaseModel):
    source: str
    target: str
    edge_type: EdgeType = EdgeType.CALLS


class GraphFragment(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    def merge(self, other: GraphFragment) -> GraphFragment:
        return GraphFragment(
            nodes=self.nodes + other.nodes,
            edges=self.edges + other.edges,
            warnings=self.warnings + other.warnings,
        )
