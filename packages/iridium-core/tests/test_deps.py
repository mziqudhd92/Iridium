"""Tests for lockfile dependency parsing."""

import json
from pathlib import Path

from iridium_core.deps.lockfiles import parse_all_lockfiles, parse_package_lock, parse_uv_lock


def test_parse_uv_lock_collects_dependencies_and_warnings(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text(
        '[[package]]\nname = "requests"\nversion = "*"\n',
        encoding="utf-8",
    )
    deps, warnings = parse_uv_lock(tmp_path)
    assert len(deps) == 1
    assert deps[0].name == "requests"
    assert any("DETERMINISM_WARNING" in w for w in warnings)


def test_parse_package_lock_v3(tmp_path: Path) -> None:
    payload = {
        "packages": {
            "": {"name": "demo-app", "version": "1.0.0"},
            "node_modules/lodash": {
                "version": "4.17.21",
                "resolved": "https://registry.npmjs.org/lodash",
            },
        }
    }
    (tmp_path / "package-lock.json").write_text(json.dumps(payload), encoding="utf-8")
    deps, warnings = parse_package_lock(tmp_path)
    assert any(dep.name == "lodash" for dep in deps)
    assert warnings == []


def test_parse_all_lockfiles_merges_sources(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text(
        '[[package]]\nname = "foo"\nversion = "1.0.0"\n', encoding="utf-8"
    )
    (tmp_path / "package-lock.json").write_text(
        json.dumps({"packages": {"node_modules/bar": {"version": "2.0.0"}}}),
        encoding="utf-8",
    )
    deps, _ = parse_all_lockfiles(tmp_path)
    names = {dep.name for dep in deps}
    assert names == {"foo", "bar"}
