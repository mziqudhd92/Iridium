"""Behavior tests for JavaScript/TypeScript regex extraction."""

from pathlib import Path

from iridium_core.extract.javascript_extractor import JavaScriptExtractor
from iridium_core.models.enums import EdgeType, NodeKind


def test_extracts_imports_routes_and_calls(tmp_path: Path) -> None:
    (tmp_path / "server.js").write_text(
        """
import express from 'express';
import type { User } from './types';
const app = express();
app.get('/api/users', (req, res) => {
  fetch('https://example.com');
});
router.use(middleware);
""",
        encoding="utf-8",
    )
    extractor = JavaScriptExtractor()
    fragment = extractor.parse_batch_safe([tmp_path / "server.js"])[0]
    kinds = {node.kind for node in fragment.nodes}
    assert NodeKind.IMPORT in kinds
    assert NodeKind.TYPE_ONLY_IMPORT in kinds
    assert NodeKind.HTTP_ROUTE in kinds
    assert NodeKind.DYNAMIC_ENTRYPOINT in kinds
    assert any(node.symbol == "express" for node in fragment.nodes)


def test_emits_route_call_and_import_edges(tmp_path: Path) -> None:
    (tmp_path / "server.js").write_text(
        """
import express from 'express';
const app = express();
app.get('/api/users', (req, res) => {
  fetch('https://example.com');
});
""",
        encoding="utf-8",
    )
    fragment = JavaScriptExtractor().parse_batch_safe([tmp_path / "server.js"])[0]
    edge_types = {edge.edge_type for edge in fragment.edges}
    assert EdgeType.ROUTES_TO in edge_types
    assert EdgeType.CALLS in edge_types
    assert EdgeType.IMPORTS in edge_types
    assert fragment.edges


def test_skips_minified_lines(tmp_path: Path) -> None:
    (tmp_path / "bundle.js").write_text("x=" + ("a" * 60_000) + "\n", encoding="utf-8")
    fragment = JavaScriptExtractor().parse_batch_safe([tmp_path / "bundle.js"])[0]
    assert any("minified" in w for w in fragment.warnings)


def test_resolve_imports_indexes_js_files(tmp_path: Path) -> None:
    (tmp_path / "util.ts").write_text("export const x = 1;\n", encoding="utf-8")
    mapping = JavaScriptExtractor().resolve_imports(tmp_path)
    assert mapping["util"] == "util.ts"
