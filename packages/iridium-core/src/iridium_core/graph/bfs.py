"""Bounded BFS traversal with hop and node caps."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

DEFAULT_MAX_HOPS = 16
DEFAULT_MAX_NODES = 50_000


@dataclass
class BfsResult:
    visited: set[str] = field(default_factory=set)
    order: list[str] = field(default_factory=list)
    truncated: bool = False
    hop_limit_hit: bool = False
    node_limit_hit: bool = False


def bounded_bfs(
    adjacency: dict[str, list[str]],
    roots: list[str],
    *,
    max_hops: int = DEFAULT_MAX_HOPS,
    max_nodes: int = DEFAULT_MAX_NODES,
) -> BfsResult:
    """Breadth-first traversal from roots with hop and visited-node caps."""
    visited: set[str] = set()
    order: list[str] = []
    queue: deque[tuple[str, int]] = deque((root, 0) for root in roots)
    hop_limit_hit = False
    node_limit_hit = False

    while queue:
        node, depth = queue.popleft()
        if node in visited:
            continue
        if len(visited) >= max_nodes:
            node_limit_hit = True
            break
        visited.add(node)
        order.append(node)

        if depth >= max_hops:
            hop_limit_hit = True
            continue

        for neighbor in adjacency.get(node, []):
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))

    return BfsResult(
        visited=visited,
        order=order,
        truncated=hop_limit_hit or node_limit_hit,
        hop_limit_hit=hop_limit_hit,
        node_limit_hit=node_limit_hit,
    )


def build_adjacency_from_edges(edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    adjacency: dict[str, list[str]] = {}
    for source, target in edges:
        adjacency.setdefault(source, []).append(target)
        adjacency.setdefault(target, [])
    return adjacency
