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
    file: str = ""
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    def merge(self, other: GraphFragment) -> GraphFragment:
        seen_nodes: set[str] = set()
        merged_nodes: list[GraphNode] = []
        for node in self.nodes + other.nodes:
            if node.id not in seen_nodes:
                seen_nodes.add(node.id)
                merged_nodes.append(node)

        seen_edges: set[tuple[str, str, EdgeType]] = set()
        merged_edges: list[GraphEdge] = []
        for edge in self.edges + other.edges:
            key = (edge.source, edge.target, edge.edge_type)
            if key not in seen_edges:
                seen_edges.add(key)
                merged_edges.append(edge)

        return GraphFragment(
            file=self.file or other.file,
            nodes=merged_nodes,
            edges=merged_edges,
            warnings=list(dict.fromkeys(self.warnings + other.warnings)),
        )
