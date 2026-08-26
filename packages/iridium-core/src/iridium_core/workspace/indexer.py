"""WorkspaceIndexer — public API for local repo indexing."""

from __future__ import annotations

import json
from pathlib import Path

from iridium_core.cache.ast_cache import AstCache, content_hash, resolve_cache_path
from iridium_core.deps.lockfiles import parse_all_lockfiles
from iridium_core.extract import DEFAULT_EXTRACTORS
from iridium_core.extract.base import LanguageExtractor
from iridium_core.git.tree_hash import git_commit_hash, git_tree_hash, repo_fingerprint
from iridium_core.graph.bfs import bounded_bfs, build_adjacency_from_edges
from iridium_core.graph.scc import collapse_scc_to_macro_nodes
from iridium_core.ignore.matcher import load_ignore_spec, should_ignore
from iridium_core.models.enums import NodeKind
from iridium_core.models.fragment import GraphFragment
from iridium_core.models.payload import ClientScanPayload
from iridium_core.sandbox.pool import run_batched


def _parse_batch_worker(paths: list[Path]) -> list[GraphFragment]:
    """Module-level worker for ProcessPoolExecutor (picklable)."""
    fragments: list[GraphFragment] = []
    ext_map: dict[str, LanguageExtractor] = {}
    for extractor in DEFAULT_EXTRACTORS:
        for ext in extractor.supported_extensions():
            ext_map[ext] = extractor

    for path in paths:
        extractor = ext_map.get(path.suffix.lower())
        if extractor:
            fragments.extend(extractor.parse_batch_safe([path]))
    return fragments


class WorkspaceIndexer:
    """Index a repository into a ClientScanPayload."""

    def __init__(
        self,
        repo: Path,
        *,
        extractors: list[LanguageExtractor] | None = None,
        use_cache: bool = True,
        use_process_pool: bool = True,
    ) -> None:
        self.repo = repo.resolve()
        self.extractors = extractors or DEFAULT_EXTRACTORS
        self.use_cache = use_cache
        self.use_process_pool = use_process_pool

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
        return sorted(files)

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

        if uncached:
            if self.use_process_pool and len(uncached) > 10:
                parsed, pool_warnings = run_batched(uncached, _parse_batch_worker)
                warnings.extend(pool_warnings)
            else:
                parsed = _parse_batch_worker(uncached)
            all_fragments.extend(parsed)

            if cache:
                for path, fragment in zip(uncached, parsed, strict=False):
                    rel = path.relative_to(self.repo).as_posix()
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

        # Build adjacency for BFS/SCC analysis
        edge_pairs = [(e.source, e.target) for e in merged.edges]
        adjacency = build_adjacency_from_edges(edge_pairs)
        if adjacency:
            collapse_scc_to_macro_nodes(adjacency)
            roots = [
                n.id
                for n in merged.nodes
                if n.kind in (NodeKind.HTTP_ROUTE, NodeKind.DYNAMIC_ENTRYPOINT)
            ]
            bfs = bounded_bfs(adjacency, roots)
            graph_truncated = bfs.truncated
        else:
            graph_truncated = False

        lang_set: set[str] = set()
        for path in files:
            if path.suffix == ".py":
                lang_set.add("python")
            elif path.suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
                lang_set.add("javascript")

        entrypoints = sum(
            1 for n in merged.nodes if n.kind in (NodeKind.HTTP_ROUTE, NodeKind.DYNAMIC_ENTRYPOINT)
        )

        return ClientScanPayload(
            repo_fingerprint=repo_fingerprint(self.repo),
            git_tree_hash=tree_hash,
            commit_hash=commit,
            languages=sorted(lang_set),
            fragments=[merged] if merged.nodes else [],
            dependencies=deps,
            graph_truncated=graph_truncated,
            determinism_warnings=[w for w in warnings if "DETERMINISM_WARNING" in w],
            supply_chain_warnings=[w for w in warnings if "DETERMINISM_WARNING" not in w],
            entrypoint_count=entrypoints,
            dependency_count=len(deps),
        )

    def dump_payload(self, *, validate: bool = False) -> str:
        payload = self.index()
        if validate:
            ClientScanPayload.model_validate(payload.model_dump())
        return payload.to_json(indent=2)
