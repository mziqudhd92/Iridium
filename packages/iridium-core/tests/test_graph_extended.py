"""Additional graph algorithm edge cases."""

from iridium_core.graph.bfs import bounded_bfs
from iridium_core.graph.scc import tarjan_scc


def test_tarjan_includes_isolated_referenced_nodes() -> None:
    adj = {"a": ["b"]}
    components = tarjan_scc(adj)
    all_nodes = {node for component in components for node in component}
    assert all_nodes == {"a", "b"}


def test_bounded_bfs_skips_revisited_nodes() -> None:
    adj = {"a": ["b"], "b": ["a"]}
    result = bounded_bfs(adj, ["a", "b"], max_hops=4, max_nodes=10)
    assert result.visited == {"a", "b"}
    assert result.truncated is False
