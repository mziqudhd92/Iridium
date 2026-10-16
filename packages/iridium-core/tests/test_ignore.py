"""Tests for .iridiumignore and default directory exclusions."""

from pathlib import Path

from iridium_core.ignore.matcher import load_ignore_spec, should_ignore


def test_default_ignore_dirs(tmp_path: Path) -> None:
    node_modules = tmp_path / "node_modules" / "pkg" / "index.js"
    node_modules.parent.mkdir(parents=True)
    node_modules.write_text("export {}\n", encoding="utf-8")
    assert should_ignore(node_modules, tmp_path, None) is True


def test_iridiumignore_patterns(tmp_path: Path) -> None:
    (tmp_path / ".iridiumignore").write_text("secrets/**\n# comment\n", encoding="utf-8")
    secret = tmp_path / "secrets" / "token.py"
    secret.parent.mkdir()
    secret.write_text("x = 1\n", encoding="utf-8")
    spec = load_ignore_spec(tmp_path)
    assert spec is not None
    assert should_ignore(secret, tmp_path, spec) is True
    assert should_ignore(tmp_path / "app.py", tmp_path, spec) is False


def test_iridiumignore_star_excludes_nested_paths(tmp_path: Path) -> None:
    """Patterns like `vendor/*` must exclude nested files (GitIgnoreSpec semantics)."""
    (tmp_path / ".iridiumignore").write_text("vendor/*\nsecrets/*\n", encoding="utf-8")
    nested = tmp_path / "vendor" / "pkg" / "mod.py"
    nested.parent.mkdir(parents=True)
    nested.write_text("x = 1\n", encoding="utf-8")
    secret = tmp_path / "secrets" / "nested" / "key.py"
    secret.parent.mkdir(parents=True)
    secret.write_text("TOKEN = 1\n", encoding="utf-8")
    spec = load_ignore_spec(tmp_path)
    assert spec is not None
    assert should_ignore(nested, tmp_path, spec) is True
    assert should_ignore(secret, tmp_path, spec) is True
    assert should_ignore(tmp_path / "app.py", tmp_path, spec) is False
