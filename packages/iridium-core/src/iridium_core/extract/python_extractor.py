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
            setattr(child, "_parent", node)


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
            if module.endswith(".__init__"):
                module = module[: -len(".__init__")]
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
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

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

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                kind = NodeKind.TYPE_ONLY_IMPORT if _is_type_only_import(node) else NodeKind.IMPORT
                nid = _node_id(rel, node.lineno, kind.value)
                nodes.append(
                    GraphNode(
                        id=nid,
                        kind=kind,
                        file=rel,
                        line=node.lineno,
                        language=self.language,
                    )
                )
                if kind == NodeKind.TYPE_ONLY_IMPORT:
                    continue

            if isinstance(node, ast.Call):
                name = _call_name(node)
                if not name:
                    continue
                dynamic = name in ("importlib.import_module", "getattr", "eval", "exec")
                indirect = bool(re.search(r"\.map\(", ast.get_source_segment(source, node) or ""))
                if dynamic:
                    kind = NodeKind.DYNAMIC_INVOCATION
                elif indirect:
                    kind = NodeKind.INDIRECT_CALL_SINK
                else:
                    kind = NodeKind.FUNCTION
                nid = _node_id(rel, node.lineno, kind.value, name)
                nodes.append(
                    GraphNode(
                        id=nid,
                        kind=kind,
                        file=rel,
                        line=node.lineno,
                        language=self.language,
                        symbol=name,
                    )
                )

            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    dec_name = ""
                    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                        dec_name = dec.func.attr
                    elif isinstance(dec, ast.Attribute):
                        dec_name = dec.attr
                    if dec_name in FLASK_ROUTE_DECORATORS:
                        nid = _node_id(rel, node.lineno, NodeKind.HTTP_ROUTE.value, node.name)
                        nodes.append(
                            GraphNode(
                                id=nid,
                                kind=NodeKind.HTTP_ROUTE,
                                file=rel,
                                line=node.lineno,
                                language=self.language,
                                symbol=node.name,
                            )
                        )
                        break

                if node.name.startswith("add_url_rule") or "add_url_rule" in node.name:
                    nid = _node_id(rel, node.lineno, NodeKind.DYNAMIC_ENTRYPOINT.value)
                    nodes.append(
                        GraphNode(
                            id=nid,
                            kind=NodeKind.DYNAMIC_ENTRYPOINT,
                            file=rel,
                            line=node.lineno,
                            language=self.language,
                        )
                    )

        return GraphFragment(nodes=nodes, edges=edges, warnings=warnings)
