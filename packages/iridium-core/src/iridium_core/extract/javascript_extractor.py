"""Basic JavaScript/TypeScript extraction (regex-based Phase 1)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from iridium_core.extract.base import ImportMap, LanguageExtractor
from iridium_core.models.enums import EdgeType, NodeKind
from iridium_core.models.fragment import GraphEdge, GraphFragment, GraphNode
from iridium_core.sanitize.scrubber import scrub_source

MAX_FILE_BYTES = 2 * 1024 * 1024
IMPORT_RE = re.compile(
    r"""(?:import\s+(?:type\s+)?[^'"]+from\s+['"]([^'"]+)['"]|"""
    r"""require\s*\(\s*['"]([^'"]+)['"]\s*\))""",
    re.MULTILINE,
)
CALL_RE = re.compile(r"\b([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*\(")
ROUTE_RE = re.compile(
    r"""(?:app|router)\.(get|post|put|delete|patch|use)\s*\(\s*['"]([^'"]+)['"]""",
    re.IGNORECASE,
)
TYPE_IMPORT_RE = re.compile(r"import\s+type\s+")


def _node_id(file: str, line: int, kind: str, symbol: str = "") -> str:
    digest = hashlib.sha256(f"{file}:{line}:{kind}:{symbol}".encode()).hexdigest()[:16]
    return f"js:{digest}"


class JavaScriptExtractor(LanguageExtractor):
    language = "javascript"

    def supported_extensions(self) -> set[str]:
        return {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}

    def resolve_imports(self, repo: Path) -> ImportMap:
        mapping: ImportMap = ImportMap()
        for path in repo.rglob("*"):
            if path.suffix not in self.supported_extensions():
                continue
            rel = path.relative_to(repo).as_posix()
            stem = path.stem
            mapping[stem] = rel
            mapping[rel] = rel
        return mapping

    def parse_batch_safe(self, paths: list[Path]) -> list[GraphFragment]:
        return [self._parse_file(path) for path in paths]

    def _add_edge(
        self,
        edges: list[GraphEdge],
        seen: set[tuple[str, str, EdgeType]],
        source: str,
        target: str,
        edge_type: EdgeType,
    ) -> None:
        key = (source, target, edge_type)
        if key in seen:
            return
        seen.add(key)
        edges.append(GraphEdge(source=source, target=target, edge_type=edge_type))

    def _parse_file(self, path: Path) -> GraphFragment:
        warnings: list[str] = []
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        seen_edges: set[tuple[str, str, EdgeType]] = set()

        try:
            raw = path.read_bytes()
        except OSError as exc:
            return GraphFragment(warnings=[f"read error {path}: {exc}"])

        if len(raw) > MAX_FILE_BYTES:
            return GraphFragment(warnings=[f"skipped oversized file: {path.name}"])

        source = scrub_source(raw.decode("utf-8", errors="ignore"))
        if any(len(line) > 50_000 for line in source.splitlines()):
            return GraphFragment(warnings=[f"skipped minified: {path.name}"])

        rel = path.as_posix()
        lines = source.splitlines()
        current_handler_id: str | None = None
        handler_indent: int | None = None
        module_import_ids: list[str] = []
        handler_ids: list[str] = []

        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            indent = len(line) - len(line.lstrip())
            if (
                current_handler_id
                and handler_indent is not None
                and indent <= handler_indent
                and not ROUTE_RE.search(line)
            ):
                current_handler_id = None
                handler_indent = None

            if TYPE_IMPORT_RE.search(line):
                nodes.append(
                    GraphNode(
                        id=_node_id(rel, lineno, NodeKind.TYPE_ONLY_IMPORT.value),
                        kind=NodeKind.TYPE_ONLY_IMPORT,
                        file=rel,
                        line=lineno,
                        language=self.language,
                    )
                )
                continue

            for match in ROUTE_RE.finditer(line):
                route = match.group(2) or ""
                route_id = _node_id(rel, lineno, NodeKind.HTTP_ROUTE.value, route)
                handler_id = _node_id(rel, lineno, NodeKind.FUNCTION.value, f"handler:{route}")
                nodes.append(
                    GraphNode(
                        id=route_id,
                        kind=NodeKind.HTTP_ROUTE,
                        file=rel,
                        line=lineno,
                        language=self.language,
                        symbol=route,
                    )
                )
                nodes.append(
                    GraphNode(
                        id=handler_id,
                        kind=NodeKind.FUNCTION,
                        file=rel,
                        line=lineno,
                        language=self.language,
                        symbol=f"handler:{route}",
                    )
                )
                self._add_edge(edges, seen_edges, route_id, handler_id, EdgeType.ROUTES_TO)
                current_handler_id = handler_id
                handler_indent = indent
                handler_ids.append(handler_id)

            for match in IMPORT_RE.finditer(line):
                specifier = match.group(1) or match.group(2) or ""
                imp_id = _node_id(rel, lineno, NodeKind.IMPORT.value, specifier)
                nodes.append(
                    GraphNode(
                        id=imp_id,
                        kind=NodeKind.IMPORT,
                        file=rel,
                        line=lineno,
                        language=self.language,
                        symbol=specifier,
                    )
                )
                if current_handler_id:
                    self._add_edge(edges, seen_edges, current_handler_id, imp_id, EdgeType.IMPORTS)
                else:
                    module_import_ids.append(imp_id)

            if "router.use(" in line or "add_url_rule" in line:
                nodes.append(
                    GraphNode(
                        id=_node_id(rel, lineno, NodeKind.DYNAMIC_ENTRYPOINT.value),
                        kind=NodeKind.DYNAMIC_ENTRYPOINT,
                        file=rel,
                        line=lineno,
                        language=self.language,
                    )
                )

            for match in CALL_RE.finditer(line):
                name = match.group(1)
                if name in ("if", "for", "while", "switch", "catch", "function"):
                    continue
                kind = NodeKind.INDIRECT_CALL_SINK if ".map(" in line else NodeKind.FUNCTION
                call_id = _node_id(rel, lineno, kind.value, name)
                nodes.append(
                    GraphNode(
                        id=call_id,
                        kind=kind,
                        file=rel,
                        line=lineno,
                        language=self.language,
                        symbol=name,
                    )
                )
                if current_handler_id:
                    self._add_edge(edges, seen_edges, current_handler_id, call_id, EdgeType.CALLS)

        for handler_id in handler_ids:
            for imp_id in module_import_ids:
                self._add_edge(edges, seen_edges, handler_id, imp_id, EdgeType.IMPORTS)

        return GraphFragment(nodes=nodes, edges=edges, warnings=warnings)
