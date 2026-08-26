"""Basic JavaScript/TypeScript extraction (regex-based Phase 1)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from iridium_core.extract.base import ImportMap, LanguageExtractor
from iridium_core.models.enums import NodeKind
from iridium_core.models.fragment import GraphFragment, GraphNode
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

    def _parse_file(self, path: Path) -> GraphFragment:
        warnings: list[str] = []
        nodes: list[GraphNode] = []

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

        for lineno, line in enumerate(lines, start=1):
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

            for match in IMPORT_RE.finditer(line):
                specifier = match.group(1) or match.group(2) or ""
                nodes.append(
                    GraphNode(
                        id=_node_id(rel, lineno, NodeKind.IMPORT.value, specifier),
                        kind=NodeKind.IMPORT,
                        file=rel,
                        line=lineno,
                        language=self.language,
                        symbol=specifier,
                    )
                )

            for match in ROUTE_RE.finditer(line):
                route = match.group(2) or ""
                nodes.append(
                    GraphNode(
                        id=_node_id(rel, lineno, NodeKind.HTTP_ROUTE.value, route),
                        kind=NodeKind.HTTP_ROUTE,
                        file=rel,
                        line=lineno,
                        language=self.language,
                        symbol=route,
                    )
                )

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
                nodes.append(
                    GraphNode(
                        id=_node_id(rel, lineno, kind.value, name),
                        kind=kind,
                        file=rel,
                        line=lineno,
                        language=self.language,
                        symbol=name,
                    )
                )

        return GraphFragment(nodes=nodes, warnings=warnings)
