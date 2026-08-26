"""Tests for graph SCC and BFS."""

from iridium_core.graph.bfs import bounded_bfs, build_adjacency_from_edges
from iridium_core.graph.scc import collapse_scc_to_macro_nodes, tarjan_scc


def test_tarjan_detects_cycle():
    adj = {
        "a": ["b"],
        "b": ["c"],
        "c": ["a"],
        "d": [],
    }
    components = tarjan_scc(adj)
    cycle = next(c for c in components if len(c) == 3)
    assert set(cycle) == {"a", "b", "c"}


def test_collapse_scc_macro_nodes():
    adj = {"a": ["b"], "b": ["a"], "c": ["a"]}
    macro_adj, mapping = collapse_scc_to_macro_nodes(adj)
    assert mapping["a"] == mapping["b"]
    assert mapping["a"] != mapping["c"]


def test_bounded_bfs_hop_limit():
    adj = {str(i): [str(i + 1)] for i in range(30)}
    adj["30"] = []
    result = bounded_bfs(adj, ["0"], max_hops=16, max_nodes=50_000)
    assert result.truncated
    assert result.hop_limit_hit
    assert len(result.visited) <= 17


def test_bounded_bfs_node_limit():
    edges = [(f"n{i}", f"n{i+1}") for i in range(100)]
    adj = build_adjacency_from_edges(edges)
    result = bounded_bfs(adj, ["n0"], max_hops=100, max_nodes=10)
    assert result.node_limit_hit
    assert len(result.visited) == 10
