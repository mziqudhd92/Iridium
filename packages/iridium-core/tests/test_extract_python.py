"""Behavior tests for Python AST extraction."""

from pathlib import Path

from iridium_core.extract.python_extractor import PythonExtractor
from iridium_core.models.enums import EdgeType, NodeKind


def test_extracts_flask_route_and_function_calls(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        """
from flask import Flask
app = Flask(__name__)

@app.route("/users")
def list_users():
  import requests
  return requests.get("http://example.com")
""",
        encoding="utf-8",
    )
    extractor = PythonExtractor()
    fragments = extractor.parse_batch_safe([tmp_path / "app.py"])
    assert len(fragments) == 1
    kinds = {node.kind for node in fragments[0].nodes}
    assert NodeKind.HTTP_ROUTE in kinds
    assert NodeKind.IMPORT in kinds
    assert any(node.symbol == "requests.get" for node in fragments[0].nodes)


def test_emits_route_call_and_import_edges(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        """
import requests

@app.route("/users")
def list_users():
    return requests.get("http://example.com")
""",
        encoding="utf-8",
    )
    fragment = PythonExtractor().parse_batch_safe([tmp_path / "app.py"])[0]
    edge_types = {edge.edge_type for edge in fragment.edges}
    assert EdgeType.ROUTES_TO in edge_types
    assert EdgeType.CALLS in edge_types
    assert EdgeType.IMPORTS in edge_types
    assert fragment.edges


def test_skips_generated_and_syntax_error_files(tmp_path: Path) -> None:
    (tmp_path / "generated.py").write_text("# auto-generated\nx = 1\n", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def oops(\n", encoding="utf-8")
    extractor = PythonExtractor()
    fragments = extractor.parse_batch_safe([tmp_path / "generated.py", tmp_path / "broken.py"])
    warnings = [w for fragment in fragments for w in fragment.warnings]
    assert any("generated" in w for w in warnings)
    assert any("syntax error" in w for w in warnings)


def test_resolve_imports_maps_modules(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "service.py").write_text("x = 1\n", encoding="utf-8")
    mapping = PythonExtractor().resolve_imports(tmp_path)
    assert mapping["pkg.service"] == "pkg/service.py"
    assert mapping["service"] == "pkg/service.py"
