"""WorkspaceIndexer — public API for local repo indexing."""

from __future__ import annotations

from functools import partial
from pathlib import Path

from iridium_core.cache.ast_cache import AstCache, content_hash, resolve_cache_path
from iridium_core.deps.lockfiles import parse_all_lockfiles
from iridium_core.extract import DEFAULT_EXTRACTORS
from iridium_core.extract.base import ImportMap, LanguageExtractor, relative_file_path
from iridium_core.git.tree_hash import git_commit_hash, git_tree_hash, repo_fingerprint
from iridium_core.graph.bfs import bounded_bfs, build_adjacency_from_edges
from iridium_core.graph.scc import collapse_scc_to_macro_nodes
from iridium_core.ignore.matcher import load_ignore_spec, should_ignore
from iridium_core.models.enums import EdgeType, NodeKind
from iridium_core.models.fragment import GraphEdge, GraphFragment, GraphNode
from iridium_core.models.payload import ClientScanPayload, DependencyNode
from iridium_core.sandbox.pool import run_batched


def _parse_batch_worker(paths: list[Path], repo: Path | None = None) -> list[GraphFragment]:
    """Module-level worker for ProcessPoolExecutor (picklable)."""
    fragments: list[GraphFragment] = []
    ext_map: dict[str, LanguageExtractor] = {}
    for extractor in DEFAULT_EXTRACTORS:
        for ext in extractor.supported_extensions():
            ext_map[ext] = extractor

    for path in paths:
        extractor = ext_map.get(path.suffix.lower())
        if extractor:
            batch_frags = extractor.parse_batch_safe([path], repo=repo)
            if batch_frags:
                fragments.extend(batch_frags)
            else:
                fragments.append(GraphFragment(file=relative_file_path(path, repo)))
    return fragments


def _link_workspace_graph(
    merged: GraphFragment,
    deps: list[DependencyNode],
    import_map: ImportMap,
) -> GraphFragment:
    """Link call sites to function definitions and imports/calls to dependency nodes."""
    if not merged.nodes:
        return merged

    nodes = list(merged.nodes)
    edges = list(merged.edges)
    seen_nodes = {n.id for n in nodes}
    seen_edges = {(e.source, e.target, e.edge_type) for e in edges}

    def _add_edge(source: str, target: str, edge_type: EdgeType) -> None:
        if source == target:
            return
        key = (source, target, edge_type)
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append(GraphEdge(source=source, target=target, edge_type=edge_type))

    # Identify function definitions (nodes that are sources of outgoing edges or routes target)
    outgoing_sources = {e.source for e in edges}
    route_targets = {e.target for e in edges if e.edge_type == EdgeType.ROUTES_TO}
    call_targets = {e.target for e in edges if e.edge_type == EdgeType.CALLS}

    defs_by_file_sym: dict[tuple[str, str], str] = {}
    defs_by_sym: dict[str, list[str]] = {}
    for node in nodes:
        if node.kind == NodeKind.FUNCTION and node.symbol:
            is_def = (
                node.id in outgoing_sources
                or node.id in route_targets
                or node.id not in call_targets
            )
            if is_def:
                defs_by_file_sym[(node.file, node.symbol)] = node.id
                defs_by_sym.setdefault(node.symbol, []).append(node.id)

    # Map known dependencies by normalized package name
    dep_names = {d.name.lower().replace("-", "_"): d.name for d in deps}
    dep_node_ids: dict[str, str] = {}

    def _ensure_dep_node(pkg_name: str, language: str) -> str:
        norm = pkg_name.lower().replace("-", "_")
        if norm in dep_node_ids:
            return dep_node_ids[norm]
        canonical = dep_names.get(norm, pkg_name)
        dep_id = f"dep:{canonical}"
        dep_node_ids[norm] = dep_id
        if dep_id not in seen_nodes:
            seen_nodes.add(dep_id)
            nodes.append(
                GraphNode(
                    id=dep_id,
                    kind=NodeKind.DEPENDENCY,
                    # Shared across files — never attribute to a single source path.
                    file="",
                    line=0,
                    language=language,
                    symbol=canonical,
                )
            )
        return dep_id

    for node in list(nodes):
        if node.kind == NodeKind.IMPORT and node.symbol:
            root_pkg = node.symbol.split(".")[0].split("/")[0].lower().replace("-", "_")
            if root_pkg in dep_names:
                dep_id = _ensure_dep_node(dep_names[root_pkg], node.language)
                _add_edge(node.id, dep_id, EdgeType.DEPENDS_ON)

        if (
            node.kind
            in (
                NodeKind.FUNCTION,
                NodeKind.DYNAMIC_INVOCATION,
                NodeKind.INDIRECT_CALL_SINK,
            )
            and node.id in call_targets
            and node.symbol
        ):
            # 1) Same-file function definition
            same_file_def = defs_by_file_sym.get((node.file, node.symbol))
            if same_file_def and same_file_def != node.id:
                _add_edge(node.id, same_file_def, EdgeType.CALLS)

            # 2) Qualified module.func call via import_map or unique workspace symbol
            parts = node.symbol.split(".")
            tail = parts[-1]
            prefix = ".".join(parts[:-1]) if len(parts) > 1 else ""
            if prefix and prefix in import_map:
                target_file = import_map[prefix]
                cross_def = defs_by_file_sym.get((target_file, tail))
                if cross_def:
                    _add_edge(node.id, cross_def, EdgeType.CALLS)
            elif not same_file_def and tail in defs_by_sym and len(defs_by_sym[tail]) == 1:
                _add_edge(node.id, defs_by_sym[tail][0], EdgeType.CALLS)

            # 3) External library call matching a declared dependency
            root_pkg = parts[0].lower().replace("-", "_")
            if root_pkg in dep_names:
                dep_id = _ensure_dep_node(dep_names[root_pkg], node.language)
                _add_edge(node.id, dep_id, EdgeType.DEPENDS_ON)

    return GraphFragment(
        file=merged.file,
        nodes=nodes,
        edges=edges,
        warnings=list(merged.warnings),
    )


class WorkspaceIndexer:
    """Index a repository into a ClientScanPayload."""

    def __init__(
        self,
        repo: Path,
        *,
        extractors: list[LanguageExtractor] | None = None,
        use_cache: bool = True,
        use_process_pool: bool = True,
        only_paths: list[Path] | None = None,
        anonymize: bool = False,
    ) -> None:
        self.repo = repo.resolve()
        self.extractors = extractors or DEFAULT_EXTRACTORS
        self.use_cache = use_cache
        self.use_process_pool = use_process_pool
        self.only_paths = [p.resolve() for p in only_paths] if only_paths else None
        self.anonymize = anonymize

    def discover_files(self) -> list[Path]:
        spec = load_ignore_spec(self.repo)
        extensions: set[str] = set()
        for extractor in self.extractors:
            extensions.update(extractor.supported_extensions())

        files: list[Path] = []
        for path in self.repo.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in extensions:
                continue
            if should_ignore(path, self.repo, spec):
                continue
            files.append(path)
        files = sorted(files)
        if self.only_paths:
            allowed = set(self.only_paths)
            files = [path for path in files if path in allowed]
        return files

    def index(self) -> ClientScanPayload:
        files = self.discover_files()
        tree_hash = git_tree_hash(self.repo)
        commit = git_commit_hash(self.repo)
        deps, dep_warnings = parse_all_lockfiles(self.repo)

        all_fragments: list[GraphFragment] = []
        warnings: list[str] = list(dep_warnings)

        cache_path = resolve_cache_path(self.repo)
        cache: AstCache | None = None
        if self.use_cache:
            cache = AstCache(cache_path)

        uncached: list[Path] = []
        if cache:
            for path in files:
                rel = path.relative_to(self.repo).as_posix()
                try:
                    raw = path.read_bytes()
                except OSError:
                    continue
                ch = content_hash(raw)
                cached = cache.get(tree_hash, rel, ch)
                if cached:
                    fragment = GraphFragment.model_validate_json(cached)
                    all_fragments.append(fragment)
                else:
                    uncached.append(path)
        else:
            uncached = files

        pool_truncated = False
        if uncached:
            worker_fn = partial(_parse_batch_worker, repo=self.repo)
            if self.use_process_pool and len(uncached) > 10:
                parsed, pool_warnings = run_batched(uncached, worker_fn)
                warnings.extend(pool_warnings)
                if any("timed out" in warning for warning in pool_warnings):
                    pool_truncated = True
            else:
                parsed = worker_fn(uncached)
            all_fragments.extend(parsed)

            if cache:
                by_file = {frag.file: frag for frag in parsed if frag.file}
                for path in uncached:
                    rel = path.relative_to(self.repo).as_posix()
                    fragment = by_file.get(rel)
                    if fragment is None:
                        if pool_truncated:
                            continue
                        fragment = GraphFragment(file=rel)
                    try:
                        raw = path.read_bytes()
                    except OSError:
                        continue
                    cache.put(
                        tree_hash,
                        rel,
                        content_hash(raw),
                        fragment.model_dump_json(),
                        commit,
                    )

        if cache:
            cache.close()

        merged = GraphFragment()
        for fragment in all_fragments:
            merged = merged.merge(fragment)
            warnings.extend(fragment.warnings)

        import_map: ImportMap = ImportMap()
        for extractor in self.extractors:
            import_map.update(extractor.resolve_imports(self.repo))
        merged = _link_workspace_graph(merged, deps, import_map)

        # Build adjacency for SCC cycle collapse and bounded BFS analysis
        edge_pairs = [(e.source, e.target) for e in merged.edges]
        adjacency = build_adjacency_from_edges(edge_pairs)
        if adjacency:
            macro_adjacency, node_to_macro = collapse_scc_to_macro_nodes(adjacency)
            roots = [
                n.id
                for n in merged.nodes
                if n.kind in (NodeKind.HTTP_ROUTE, NodeKind.DYNAMIC_ENTRYPOINT)
            ]
            bfs = bounded_bfs(adjacency, roots)
            macro_roots = list(dict.fromkeys(node_to_macro.get(r, r) for r in roots))
            macro_bfs = bounded_bfs(macro_adjacency, macro_roots)
            graph_truncated = bfs.truncated or macro_bfs.truncated or pool_truncated
        else:
            graph_truncated = pool_truncated

        lang_set: set[str] = set()
        for path in files:
            if path.suffix.lower() in {".py", ".pyw"}:
                lang_set.add("python")
            elif path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
                lang_set.add("javascript")

        entrypoints = sum(
            1 for n in merged.nodes if n.kind in (NodeKind.HTTP_ROUTE, NodeKind.DYNAMIC_ENTRYPOINT)
        )

        payload = ClientScanPayload(
            repo_fingerprint=repo_fingerprint(self.repo),
            git_tree_hash=tree_hash,
            commit_hash=commit,
            languages=sorted(lang_set),
            fragments=[merged] if merged.nodes else [],
            dependencies=deps,
            graph_truncated=graph_truncated,
            determinism_warnings=list(
                dict.fromkeys(w for w in warnings if "DETERMINISM_WARNING" in w)
            ),
            supply_chain_warnings=list(
                dict.fromkeys(w for w in warnings if "DETERMINISM_WARNING" not in w)
            ),
            entrypoint_count=entrypoints,
            dependency_count=len(deps),
        )
        return payload.anonymize() if self.anonymize else payload

    def dump_payload(self, *, validate: bool = False) -> str:
        payload = self.index()
        if validate:
            ClientScanPayload.model_validate(payload.model_dump())
        return payload.to_json(indent=2)
