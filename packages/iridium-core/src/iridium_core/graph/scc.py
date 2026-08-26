"""Tarjan strongly-connected components for cycle collapse."""

from __future__ import annotations

from collections import defaultdict


def tarjan_scc(adjacency: dict[str, list[str]]) -> list[list[str]]:
    """Return strongly connected components as lists of node ids."""
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in adjacency.get(node, []):
            if neighbor not in indices:
                strongconnect(neighbor)
                lowlink[node] = min(lowlink[node], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[node] = min(lowlink[node], indices[neighbor])

        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == node:
                    break
            components.append(component)

    for node in adjacency:
        if node not in indices:
            strongconnect(node)

    # Include isolated nodes not present as keys but referenced
    referenced: set[str] = set(adjacency)
    for targets in adjacency.values():
        referenced.update(targets)
    for node in referenced:
        if node not in indices:
            components.append([node])

    return components


def collapse_scc_to_macro_nodes(
    adjacency: dict[str, list[str]],
) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Collapse SCCs into macro-nodes; return new adjacency and node→macro mapping."""
    components = tarjan_scc(adjacency)
    node_to_macro: dict[str, str] = {}
    macro_adjacency: dict[str, list[str]] = defaultdict(list)

    for idx, component in enumerate(components):
        macro_id = f"scc:{idx}"
        for node in component:
            node_to_macro[node] = macro_id

    for source, targets in adjacency.items():
        macro_source = node_to_macro.get(source, source)
        for target in targets:
            macro_target = node_to_macro.get(target, target)
            if macro_source != macro_target:
                macro_adjacency[macro_source].append(macro_target)

    # Deduplicate target lists
    return {k: sorted(set(v)) for k, v in macro_adjacency.items()}, node_to_macro
