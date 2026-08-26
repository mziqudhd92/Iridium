"""Lockfile parsers for dependency resolution."""

from __future__ import annotations

import json
import re
from pathlib import Path

from iridium_core.models.payload import DependencyNode

DETERMINISM_PATTERNS = (r"\*", r"latest", r"^$")


def parse_uv_lock(repo: Path) -> tuple[list[DependencyNode], list[str]]:
    """Parse uv.lock TOML-like format (basic)."""
    lock_path = repo / "uv.lock"
    if not lock_path.is_file():
        return [], []

    warnings: list[str] = []
    deps: list[DependencyNode] = []
    try:
        text = lock_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return [], []

    current_name: str | None = None
    current_version: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("name ="):
            current_name = stripped.split("=", 1)[1].strip().strip('"')
        elif stripped.startswith("version =") and current_name:
            current_version = stripped.split("=", 1)[1].strip().strip('"')
            deps.append(
                DependencyNode(name=current_name, version=current_version, ecosystem="pypi")
            )
            current_name = None
            current_version = None

    for dep in deps:
        if dep.version and any(
            re.search(p, dep.version, re.IGNORECASE) for p in DETERMINISM_PATTERNS
        ):
            warnings.append(f"DETERMINISM_WARNING: unpinned {dep.name}={dep.version} in uv.lock")

    return deps, warnings


def parse_package_lock(repo: Path) -> tuple[list[DependencyNode], list[str]]:
    """Parse package-lock.json v2/v3 dependencies (basic)."""
    lock_path = repo / "package-lock.json"
    if not lock_path.is_file():
        return [], []

    warnings: list[str] = []
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, json.JSONDecodeError):
        return [], []

    packages = payload.get("packages") or {}
    deps: list[DependencyNode] = []
    for pkg_path, meta in packages.items():
        if not isinstance(meta, dict):
            continue
        name = meta.get("name") or (pkg_path.split("node_modules/")[-1] if pkg_path else "")
        if not name or name.startswith("node_modules"):
            continue
        version = meta.get("version")
        resolved = meta.get("resolved")
        if version:
            deps.append(
                DependencyNode(
                    name=name,
                    version=version,
                    ecosystem="npm",
                    resolved_url=resolved,
                )
            )
            if any(re.search(p, str(version), re.IGNORECASE) for p in DETERMINISM_PATTERNS):
                warnings.append(
                    f"DETERMINISM_WARNING: unpinned {name}={version} in package-lock.json"
                )

    return deps, warnings


def parse_all_lockfiles(repo: Path) -> tuple[list[DependencyNode], list[str]]:
    """Parse available lockfiles; uv.lock takes precedence over manifests."""
    all_deps: list[DependencyNode] = []
    all_warnings: list[str] = []

    uv_deps, uv_warn = parse_uv_lock(repo)
    all_deps.extend(uv_deps)
    all_warnings.extend(uv_warn)

    npm_deps, npm_warn = parse_package_lock(repo)
    all_deps.extend(npm_deps)
    all_warnings.extend(npm_warn)

    return all_deps, all_warnings
