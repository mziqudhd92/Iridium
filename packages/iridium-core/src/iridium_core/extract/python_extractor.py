"""Python AST extraction plugin."""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

from iridium_core.extract.base import ImportMap, LanguageExtractor
from iridium_core.models.enums import EdgeType, NodeKind
from iridium_core.models.fragment import GraphEdge, GraphFragment, GraphNode
from iridium_core.sanitize.scrubber import scrub_source

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_AST_DEPTH = 256
GENERATED_MARKERS = ("@generated", "# generated", "# auto-generated")
FLASK_ROUTE_DECORATORS = ("route", "get", "post", "put", "delete", "patch")


def _node_id(file: str, line: int, kind: str, symbol: str = "") -> str:
    digest = hashlib.sha256(f"{file}:{line}:{kind}:{symbol}".encode()).hexdigest()[:16]
    return f"py:{digest}"


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        parts: list[str] = []
        current: ast.AST = func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    return ""


def _ast_depth(node: ast.AST, depth: int = 0) -> int:
    if depth > MAX_AST_DEPTH:
        return depth
    max_child = depth
    for child in ast.iter_child_nodes(node):
        max_child = max(max_child, _ast_depth(child, depth + 1))
    return max_child


def _is_generated_or_minified(source: str) -> bool:
    lowered = source[:500].lower()
    if any(marker in lowered for marker in GENERATED_MARKERS):
        return True
    for line in source.splitlines():
        if len(line) > 50_000:
            return True
    return False


def _is_type_only_import(node: ast.Import | ast.ImportFrom) -> bool:
    parent = getattr(node, "_parent", None)
    while parent is not None:
        if isinstance(parent, ast.If):
            test = parent.test
            if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
                return True
            if isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING":
                return True
        parent = getattr(parent, "_parent", None)
    return False


def _annotate_parents(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._parent = node


def _route_decorator_name(dec: ast.expr) -> str:
    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
        return dec.func.attr
    if isinstance(dec, ast.Attribute):
        return dec.attr
    return ""


class _PythonFileVisitor(ast.NodeVisitor):
    def __init__(self, *, rel: str, source: str, language: str) -> None:
        self.rel = rel
        self.source = source
        self.language = language
        self.nodes: list[GraphNode] = []
        self.edges: list[GraphEdge] = []
        self.current_function_id: str | None = None
        self.module_import_ids: list[str] = []
        self.function_ids: list[str] = []
        self._seen_edges: set[tuple[str, str, EdgeType]] = set()

    def _add_edge(self, source: str, target: str, edge_type: EdgeType) -> None:
        key = (source, target, edge_type)
        if key in self._seen_edges:
            return
        self._seen_edges.add(key)
        self.edges.append(GraphEdge(source=source, target=target, edge_type=edge_type))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        func_id = _node_id(self.rel, node.lineno, NodeKind.FUNCTION.value, node.name)
        self.nodes.append(
            GraphNode(
                id=func_id,
                kind=NodeKind.FUNCTION,
                file=self.rel,
                line=node.lineno,
                language=self.language,
                symbol=node.name,
            )
        )
        self.function_ids.append(func_id)

        for dec in node.decorator_list:
            if _route_decorator_name(dec) in FLASK_ROUTE_DECORATORS:
                route_id = _node_id(self.rel, node.lineno, NodeKind.HTTP_ROUTE.value, node.name)
                self.nodes.append(
                    GraphNode(
                        id=route_id,
                        kind=NodeKind.HTTP_ROUTE,
                        file=self.rel,
                        line=node.lineno,
                        language=self.language,
                        symbol=node.name,
                    )
                )
                self._add_edge(route_id, func_id, EdgeType.ROUTES_TO)
                break

        if node.name.startswith("add_url_rule") or "add_url_rule" in node.name:
            entry_id = _node_id(self.rel, node.lineno, NodeKind.DYNAMIC_ENTRYPOINT.value)
            self.nodes.append(
                GraphNode(
                    id=entry_id,
                    kind=NodeKind.DYNAMIC_ENTRYPOINT,
                    file=self.rel,
                    line=node.lineno,
                    language=self.language,
                )
            )

        previous = self.current_function_id
        self.current_function_id = func_id
        self.generic_visit(node)
        self.current_function_id = previous

    def visit_Import(self, node: ast.Import) -> None:
        self._visit_import(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self._visit_import(node)

    def _visit_import(self, node: ast.Import | ast.ImportFrom) -> None:
        kind = NodeKind.TYPE_ONLY_IMPORT if _is_type_only_import(node) else NodeKind.IMPORT
        symbol = ""
        if isinstance(node, ast.Import):
            if node.names:
                symbol = node.names[0].name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            symbol = node.module.split(".")[0]
        nid = _node_id(self.rel, node.lineno, kind.value, symbol)
        self.nodes.append(
            GraphNode(
                id=nid,
                kind=kind,
                file=self.rel,
                line=node.lineno,
                language=self.language,
                symbol=symbol,
            )
        )
        if kind == NodeKind.TYPE_ONLY_IMPORT:
            return
        if self.current_function_id:
            self._add_edge(self.current_function_id, nid, EdgeType.IMPORTS)
        else:
            self.module_import_ids.append(nid)

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node)
        if not name:
            self.generic_visit(node)
            return
        dynamic = name in ("importlib.import_module", "getattr", "eval", "exec")
        indirect = bool(re.search(r"\.map\(", ast.get_source_segment(self.source, node) or ""))
        if dynamic:
            kind = NodeKind.DYNAMIC_INVOCATION
        elif indirect:
            kind = NodeKind.INDIRECT_CALL_SINK
        else:
            kind = NodeKind.FUNCTION
        nid = _node_id(self.rel, node.lineno, kind.value, name)
        self.nodes.append(
            GraphNode(
                id=nid,
                kind=kind,
                file=self.rel,
                line=node.lineno,
                language=self.language,
                symbol=name,
            )
        )
        if self.current_function_id:
            self._add_edge(self.current_function_id, nid, EdgeType.CALLS)
        self.generic_visit(node)

    def finalize(self) -> None:
        for func_id in self.function_ids:
            for imp_id in self.module_import_ids:
                self._add_edge(func_id, imp_id, EdgeType.IMPORTS)


class PythonExtractor(LanguageExtractor):
    language = "python"

    def supported_extensions(self) -> set[str]:
        return {".py", ".pyw"}

    def resolve_imports(self, repo: Path) -> ImportMap:
        mapping: ImportMap = ImportMap()
        for path in repo.rglob("*.py"):
            if not path.is_file():
                continue
            rel = path.relative_to(repo).as_posix()
            module = rel[:-3].replace("/", ".")
            module = module.removesuffix(".__init__")
            mapping[module] = rel
            parts = module.split(".")
            if parts:
                mapping[parts[-1]] = rel
        return mapping

    def parse_batch_safe(self, paths: list[Path]) -> list[GraphFragment]:
        fragments: list[GraphFragment] = []
        for path in paths:
            fragment = self._parse_file(path)
            if fragment.nodes or fragment.edges or fragment.warnings:
                fragments.append(fragment)
        return fragments

    def _parse_file(self, path: Path) -> GraphFragment:
        warnings: list[str] = []

        try:
            raw = path.read_bytes()
        except OSError as exc:
            return GraphFragment(warnings=[f"read error {path}: {exc}"])

        if len(raw) > MAX_FILE_BYTES:
            return GraphFragment(warnings=[f"skipped oversized file: {path.name}"])

        source = raw.decode("utf-8", errors="ignore")
        if _is_generated_or_minified(source):
            return GraphFragment(warnings=[f"skipped generated/minified: {path.name}"])

        source = scrub_source(source)
        rel = path.as_posix()

        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return GraphFragment(warnings=[f"syntax error {path.name}: {exc.msg}"])

        _annotate_parents(tree)
        if _ast_depth(tree) > MAX_AST_DEPTH:
            warnings.append(f"AST depth cap exceeded: {path.name}")

        visitor = _PythonFileVisitor(rel=rel, source=source, language=self.language)
        visitor.visit(tree)
        visitor.finalize()
        return GraphFragment(nodes=visitor.nodes, edges=visitor.edges, warnings=warnings)
