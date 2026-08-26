"""Graph algorithms."""

from iridium_core.graph.bfs import BfsResult, bounded_bfs, build_adjacency_from_edges
from iridium_core.graph.scc import collapse_scc_to_macro_nodes, tarjan_scc

__all__ = [
    "BfsResult",
    "bounded_bfs",
    "build_adjacency_from_edges",
    "collapse_scc_to_macro_nodes",
    "tarjan_scc",
]
